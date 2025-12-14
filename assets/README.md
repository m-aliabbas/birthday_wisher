# Assets Folder

## Logo Setup

To add the City Bakers logo to the intro animation:

1. Place your logo file in this directory as `logo.png`
2. Recommended formats: PNG with transparent background
3. Recommended size: At least 500x500 pixels for best quality
4. The logo will automatically:
   - Scale to 15% of video height
   - Maintain aspect ratio
   - Position at bottom center
   - Fade in/out with the intro
   - Have a subtle glow effect

## File Naming

The intro generator will look for these files in order:
- `assets/logo.png` (recommended)
- `assets/city_bakers_logo.png`
- `logo.png` (in root directory)
- `templates/logo.png`

If no logo is found, the intro will still work beautifully without it.

## Logo Design Tips

For best results, your logo should:
- Have a transparent background (PNG format)
- Be high resolution (at least 500px on the smallest dimension)
- Work well on dark backgrounds (the intro uses #1a1a2e background)
- Have good contrast with the purple gradient overlay
