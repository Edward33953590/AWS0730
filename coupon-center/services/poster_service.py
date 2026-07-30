"""Poster generation service - combine background images with marketing copy."""
import os
import io
import uuid
import base64
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Directory where poster assets are stored
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'poster_assets')
# Directory for generated posters
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'generated_posters')


def _ensure_output_dir():
    """Ensure the output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def _hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_poster(asset_id, title, description, slogan='', campaign_name=''):
    """
    Generate a coupon poster by overlaying text on a background image.

    Args:
        asset_id: PosterAsset ID from database
        title: Main headline text
        description: Description text
        slogan: Optional short slogan
        campaign_name: Optional campaign name for the poster

    Returns:
        (result_dict, error_string)
        result_dict contains: filename, url, base64_preview
    """
    from models.poster_asset import PosterAsset

    # Get asset from database
    asset = PosterAsset.query.get(asset_id)
    if not asset:
        return None, '海报资源不存在'

    if not asset.is_active:
        return None, '该海报资源已停用'

    # Check if the background image file exists
    bg_path = os.path.join(ASSETS_DIR, asset.filename)
    if not os.path.exists(bg_path):
        return None, f'背景图文件不存在: {asset.filename}'

    try:
        result = _render_poster(
            bg_path=bg_path,
            text_area=asset.text_area,
            text_color=asset.text_color,
            font_size=asset.recommended_font_size,
            title=title,
            description=description,
            slogan=slogan,
            campaign_name=campaign_name,
        )
        return result, None
    except ImportError:
        # Pillow not installed - use fallback
        logger.warning('Pillow not installed, using text-only fallback')
        return _fallback_poster(asset, title, description, slogan), None
    except Exception as e:
        logger.error(f'Poster generation failed: {e}')
        return None, f'海报生成失败: {str(e)}'


def _render_poster(bg_path, text_area, text_color, font_size, title, description, slogan, campaign_name):
    """Render poster using Pillow (PIL)."""
    from PIL import Image, ImageDraw, ImageFont

    # Open background image
    img = Image.open(bg_path).convert('RGBA')

    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Try to load a Chinese-compatible font, fall back to default
    font_title = _get_font(font_size + 4)
    font_body = _get_font(font_size)
    font_slogan = _get_font(font_size - 4)

    # Parse text area
    x = text_area.get('x', 50)
    y = text_area.get('y', 50)
    max_width = text_area.get('width', 400)
    max_height = text_area.get('height', 200)

    color = _hex_to_rgb(text_color)

    # Draw title
    current_y = y
    if campaign_name:
        _draw_wrapped_text(draw, campaign_name, x, current_y, max_width, font_slogan, color + (180,))
        current_y += font_size

    # Draw main title (bold/larger)
    _draw_wrapped_text(draw, title, x, current_y, max_width, font_title, color + (255,))
    current_y += int(font_size * 1.8)

    # Draw description
    if description:
        _draw_wrapped_text(draw, description, x, current_y, max_width, font_body, color + (220,))
        current_y += int(font_size * 2.2)

    # Draw slogan
    if slogan:
        _draw_wrapped_text(draw, slogan, x, current_y, max_width, font_slogan, color + (200,))

    # Save to output directory
    _ensure_output_dir()
    output_filename = f'poster_{uuid.uuid4().hex[:8]}_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Convert to RGB for saving as PNG (remove alpha if not needed)
    output_img = img.convert('RGB')
    output_img.save(output_path, 'PNG', quality=95)

    # Generate base64 preview (smaller size for API response)
    preview_img = output_img.copy()
    preview_img.thumbnail((600, 800))
    buffer = io.BytesIO()
    preview_img.save(buffer, format='PNG')
    base64_preview = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return {
        'filename': output_filename,
        'url': f'/static/generated_posters/{output_filename}',
        'base64_preview': f'data:image/png;base64,{base64_preview}',
    }


def _get_font(size):
    """Try to load a suitable font for Chinese text rendering."""
    from PIL import ImageFont

    # Common Chinese font paths on different OS
    font_paths = [
        # Windows
        'C:/Windows/Fonts/msyh.ttc',       # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',     # 黑体
        'C:/Windows/Fonts/simsun.ttc',     # 宋体
        # macOS
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        # Linux
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # Fall back to Pillow default font
    try:
        return ImageFont.truetype('arial.ttf', size)
    except Exception:
        return ImageFont.load_default()


def _draw_wrapped_text(draw, text, x, y, max_width, font, color):
    """Draw text with word wrapping within max_width."""
    if not text:
        return y

    lines = []
    current_line = ''

    for char in text:
        test_line = current_line + char
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0] if bbox else 0

        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    # Draw each line
    line_height = font.size if hasattr(font, 'size') else 20
    try:
        bbox = font.getbbox('测')
        line_height = (bbox[3] - bbox[1]) + 4
    except Exception:
        line_height = 24

    for line in lines:
        draw.text((x, y), line, fill=color, font=font)
        y += line_height

    return y


def _fallback_poster(asset, title, description, slogan):
    """Fallback when Pillow is not available - return metadata only."""
    return {
        'filename': None,
        'url': asset.image_url,
        'base64_preview': None,
        'fallback': True,
        'overlay_text': {
            'title': title,
            'description': description,
            'slogan': slogan,
            'text_area': asset.text_area,
            'text_color': asset.text_color,
            'font_size': asset.recommended_font_size,
        },
        'message': '图片合成服务不可用，请安装 Pillow 依赖。当前返回文案和背景图信息供前端渲染。',
    }


def get_poster_assets(category=None, style=None):
    """
    Get available poster assets list.

    Args:
        category: Filter by category (optional)
        style: Filter by style (optional)

    Returns:
        List of asset dicts
    """
    from models.poster_asset import PosterAsset

    query = PosterAsset.query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)
    if style:
        query = query.filter_by(style=style)

    assets = query.order_by(PosterAsset.created_at.desc()).all()
    return [a.to_dict() for a in assets]


def generate_poster_with_ai_copy(asset_id, coupon_type, params, context='', campaign_name=''):
    """
    Generate a poster using AI-generated copy combined with a background image.
    This is the main entry point for the operator workflow.

    Args:
        asset_id: Background image asset ID
        coupon_type: Type of coupon (for AI copy generation)
        params: Coupon parameters (for AI copy generation)
        context: Additional context for AI copy
        campaign_name: Campaign name to display

    Returns:
        (result_dict, error_string)
    """
    from services.ai_copy_service import generate_copy

    # Step 1: Generate marketing copy via AI
    copy_result = generate_copy(coupon_type, params, context)

    title = copy_result.get('title', '')
    description = copy_result.get('description', '')
    slogan = copy_result.get('slogan', '')

    # Step 2: Generate poster with the copy
    poster_result, error = generate_poster(
        asset_id=asset_id,
        title=title,
        description=description,
        slogan=slogan,
        campaign_name=campaign_name,
    )

    if error:
        return None, error

    # Merge copy info into result
    poster_result['copy'] = copy_result
    return poster_result, None
