from pathlib import Path
import shutil
root=Path(__file__).resolve().parent
dist=root/'dist'
if dist.exists(): shutil.rmtree(dist)
dist.mkdir()
for name in ['index.html','app.js','styles.css','service-worker.js','manifest.webmanifest','icon-192.png','icon-512.png','history.csv','data-status.json']:
    shutil.copy2(root/name,dist/name)
