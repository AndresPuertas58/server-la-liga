# nsfw_validator_strict.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageFilter
import io
import numpy as np
from typing import Dict, List, Tuple
import uvicorn
import logging
import math

app = FastAPI(title="NSFW Validator Strict")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StrictNSFWValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Umbrales más estrictos
        self.SKIN_THRESHOLD = 25  # % máximo de piel (antes 40)
        self.ASPECT_RATIO_MAX = 2.5
        self.ASPECT_RATIO_MIN = 0.4
        self.MIN_RESOLUTION = 200  # ancho/alto mínimo
        self.CONTRAST_THRESHOLD = 0.4
        
    def validate_image(self, image_data: bytes) -> Dict:
        """
        Valida imagen con reglas más estrictas
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            file_size = len(image_data)
            aspect_ratio = width / height
            
            img_array = np.array(image)
            
            # Múltiples análisis
            skin_percentage = self._analyze_skin_tone(img_array)
            contrast_score = self._calculate_contrast(img_array)
            brightness_score = self._calculate_brightness(img_array)
            edge_density = self._analyze_edges(img_array)
            color_variance = self._analyze_color_variance(img_array)
            saturation_score = self._analyze_saturation(img_array)
            
            # Reglas de validación MÁS ESTRICTAS
            violations = []
            risk_score = 0
            
            # 1. Análisis de tonos de piel
            if skin_percentage > self.SKIN_THRESHOLD:
                risk_score += 30
                violations.append(f"Alto contenido de tonos de piel ({skin_percentage:.1f}%)")
            
            # 2. Relación de aspecto (selfies, poses)
            if aspect_ratio > self.ASPECT_RATIO_MAX or aspect_ratio < self.ASPECT_RATIO_MIN:
                risk_score += 20
                violations.append(f"Relación de aspecto sospechosa: {aspect_ratio:.2f}")
            
            # 3. Resolución
            if width < self.MIN_RESOLUTION or height < self.MIN_RESOLUTION:
                risk_score += 15
                violations.append("Resolución muy baja (posible thumbnail explícito)")
            
            # 4. Contraste (imágenes muy contrastadas)
            if contrast_score > self.CONTRAST_THRESHOLD:
                risk_score += 10
                violations.append(f"Contraste muy alto: {contrast_score:.3f}")
            
            # 5. Brillo (imágenes muy oscuras o claras)
            if brightness_score < 0.2 or brightness_score > 0.8:
                risk_score += 10
                violations.append(f"Brillo fuera de rango normal: {brightness_score:.3f}")
            
            # 6. Densidad de bordes (detalle anatómico)
            if edge_density > 0.15 and skin_percentage > 15:
                risk_score += 15
                violations.append(f"Alto detalle anatómico detectado")
            
            # 7. Imágenes mayormente de un color (posibles desnudos)
            if color_variance < 0.1 and skin_percentage > 20:
                risk_score += 10
                violations.append("Baja variación de colores con alto contenido de piel")
            
            # 8. Saturación (imágenes muy saturadas)
            if saturation_score > 0.7:
                risk_score += 5
                violations.append(f"Saturación muy alta: {saturation_score:.3f}")
            
            # Calcular probabilidades
            risk_score = min(100, risk_score)
            safe_confidence = max(0.1, (100 - risk_score) / 100)
            nsfw_confidence = 1.0 - safe_confidence
            
            # Aprobar solo si riesgo es bajo
            is_safe = risk_score < 40  # Solo aprueba si riesgo < 40%
            
            return {
                'approved': is_safe,
                'is_safe': is_safe,
                'safe_confidence': safe_confidence,
                'nsfw_confidence': nsfw_confidence,
                'risk_score': risk_score,
                'violations': violations,
                'image_analysis': {
                    'width': width,
                    'height': height,
                    'file_size_kb': round(file_size / 1024, 1),
                    'skin_percentage': round(skin_percentage, 2),
                    'aspect_ratio': round(aspect_ratio, 2),
                    'contrast_score': round(contrast_score, 3),
                    'brightness_score': round(brightness_score, 3),
                    'edge_density': round(edge_density, 3),
                    'color_variance': round(color_variance, 3),
                    'saturation_score': round(saturation_score, 3)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error validando imagen: {e}")
            return {
                'approved': False,
                'is_safe': False,
                'safe_confidence': 0.0,
                'nsfw_confidence': 1.0,
                'risk_score': 100,
                'violations': ['Error procesando imagen'],
                'error': str(e)
            }
    
    def _analyze_skin_tone(self, img_array: np.ndarray) -> float:
        """Análisis mejorado de tonos de piel"""
        r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]
        
        # Múltiples rangos para diferentes tonos de piel
        skin_mask1 = (
            (r > 95) & (g > 40) & (b > 20) &
            ((r - g) > 15) & (r > g) & (r > b) &
            (np.maximum.reduce([r, g, b]) - np.minimum.reduce([r, g, b]) > 15) &
            (abs(r - g) > 15)
        )
        
        # Rangos para tonos más claros
        skin_mask2 = (
            (r > 200) & (g > 180) & (b > 160) &
            (abs(r - g) < 30) & (abs(r - b) < 30) & (abs(g - b) < 30)
        )
        
        # Combinar máscaras
        skin_mask = skin_mask1 | skin_mask2
        total_pixels = img_array.shape[0] * img_array.shape[1]
        
        return (np.sum(skin_mask) / total_pixels) * 100
    
    def _calculate_contrast(self, img_array: np.ndarray) -> float:
        """Calcula contraste usando desviación estándar"""
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        return np.std(gray) / 255.0
    
    def _calculate_brightness(self, img_array: np.ndarray) -> float:
        """Calcula brillo promedio"""
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
        return np.mean(gray) / 255.0
    
    def _analyze_edges(self, img_array: np.ndarray) -> float:
        """Analiza densidad de bordes (detalle anatómico)"""
        gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)
        
        # Simular detección de bordes simple
        from scipy import ndimage
        dx = ndimage.sobel(gray, 0)  # Derivada horizontal
        dy = ndimage.sobel(gray, 1)  # Derivada vertical
        mag = np.hypot(dx, dy)
        
        edge_density = np.sum(mag > 50) / mag.size  # Umbral empírico
        return edge_density
    
    def _analyze_color_variance(self, img_array: np.ndarray) -> float:
        """Analiza variación de colores"""
        # Convertir a HSV para mejor análisis
        hsv = self._rgb_to_hsv(img_array)
        hue_variance = np.std(hsv[:,:,0]) / 180.0  # Normalizar
        return hue_variance
    
    def _analyze_saturation(self, img_array: np.ndarray) -> float:
        """Analiza saturación promedio"""
        hsv = self._rgb_to_hsv(img_array)
        return np.mean(hsv[:,:,1])
    
    def _rgb_to_hsv(self, img_array: np.ndarray) -> np.ndarray:
        """Convierte RGB a HSV manualmente"""
        r, g, b = img_array[:,:,0]/255.0, img_array[:,:,1]/255.0, img_array[:,:,2]/255.0
        
        maxc = np.maximum.reduce([r, g, b])
        minc = np.minimum.reduce([r, g, b])
        
        v = maxc
        
        deltac = maxc - minc
        s = np.where(maxc != 0, deltac / maxc, 0)
        
        # Hue calculation
        rc = np.where(maxc != 0, (maxc - r) / deltac, 0)
        gc = np.where(maxc != 0, (maxc - g) / deltac, 0)
        bc = np.where(maxc != 0, (maxc - b) / deltac, 0)
        
        h = np.where(maxc == r, bc - gc, 
                    np.where(maxc == g, 2.0 + rc - bc, 
                            4.0 + gc - rc))
        h = (h / 6.0) % 1.0
        
        return np.stack([h, s, v], axis=2)

validator = StrictNSFWValidator()

@app.post("/validate")
async def validate_image(file: UploadFile = File(...)) -> Dict:
    try:
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(400, "Tipo de archivo no permitido")
        
        max_size = 10 * 1024 * 1024
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(400, "Imagen demasiado grande. Máximo 10MB")
        
        result = validator.validate_image(contents)
        
        return {
            "filename": file.filename,
            "validation_passed": result['approved'],
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error validando imagen: {e}")
        raise HTTPException(500, "Error interno del servidor")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "NSFW Validator Strict"}

if __name__ == "__main__":
    print("🚀 Iniciando NSFW Validator STRICT en http://localhost:8000")
    print("🔒 Este validador es más estricto y detecta más contenido inapropiado")
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")