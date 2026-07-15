import easyocr
from app.schemas.ocr import OcrResponse, OcrBlock, BoundingBox

class OcrClient:
    def __init__(self):
        print("📦 [OCR] 무료 로컬 EasyOCR 모델을 로딩합니다...")
        # 최초 실행 시 모델 가중치 파일(.pth)을 다운로드하므로 시간이 조금 걸립니다.
        self.reader = easyocr.Reader(['ko', 'en'], gpu=False)
        print("✅ [OCR] EasyOCR 로딩 완료!")

    async def extract(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        # EasyOCR로 텍스트 인식 수행
        results = self.reader.readtext(content)
        
        full_texts = []
        blocks = []
        
        for bbox, text, conf in results:
            full_texts.append(text)
            
            # 바운딩 박스를 사용하는 경우 임시 좌표 전달
            box = None
            if include_bounding_boxes:
                box = BoundingBox(x=0.0, y=0.0, width=0.0, height=0.0)
                
            blocks.append(
                OcrBlock(
                    text=text,
                    confidence=min(1.0,float(conf)),
                    bounding_box=box
                )
            )
            
        return OcrResponse(
            text=" ".join(full_texts),
            blocks=blocks,
            model_version="easyocr-free-v1"
        )