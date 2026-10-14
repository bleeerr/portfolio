"""Rebuild responsive WebP images from preserved original JPEGs (Pillow)."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent.parent
for folder in sorted((root/'assets/projects').iterdir()):
 if not folder.is_dir():continue
 destination=root/'public/media'/folder.name
 destination.mkdir(parents=True,exist_ok=True)
 for n,source in enumerate(sorted(folder.glob('*.jpg')),1):
  with Image.open(source) as image:
   image.thumbnail((1600,1600))
   image.save(destination/f'{folder.name}_{n:02}.webp','WEBP',quality=85)
print('WebP previews rebuilt; original JPG files preserved')
