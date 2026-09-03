import json
from pathlib import Path

def test_models():
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ultralytics not installed yet")
        return

    models_dir = Path("models")
    results = {}
    
    for d in models_dir.iterdir():
        if d.is_dir() and (d / "best.pt").exists():
            model_path = d / "best.pt"
            try:
                model = YOLO(str(model_path))
                results[d.name] = model.names
            except Exception as e:
                results[d.name] = f"Error: {str(e)}"
                
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_models()
