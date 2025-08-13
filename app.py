#!/usr/bin/env python3

"""
Simple yt-dlp API service for bypassing YouTube restrictions
Deploy this to Railway, Render, or any Python hosting platform
"""

from flask import Flask, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple API key authentication (optional)
API_KEY = os.environ.get('API_KEY', 'your-secret-key-123')

def authenticate(req):
    """Simple API key authentication"""
    api_key = req.headers.get('Authorization', '').replace('Bearer ', '')
    return api_key == API_KEY

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'yt-dlp API',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/download', methods=['POST'])
def download():
    """Download audio from YouTube video"""
    try:
        # Optional authentication
        if API_KEY and API_KEY != 'your-secret-key-123':
            if not authenticate(request):
                return jsonify({'error': 'Invalid API key'}), 401

        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL required in JSON body'}), 400

        url = data['url']
        format_selector = data.get('format', 'bestaudio')
        
        logger.info(f"Processing download request for: {url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, '%(id)s.%(ext)s')
            
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_path,
                'extractaudio': True,
                'audioformat': 'webm',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                # Anti-detection headers
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(url, download=False)
                video_id = info.get('id', 'unknown')
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                
                logger.info(f"Video info: {title} ({duration}s)")
                
                # Download the audio
                ydl.download([url])
                
                # Find the downloaded file
                files = os.listdir(temp_dir)
                if not files:
                    return jsonify({'error': 'Download failed - no files created'}), 500
                
                downloaded_file = os.path.join(temp_dir, files[0])
                file_size = os.path.getsize(downloaded_file)
                
                logger.info(f"Download successful: {file_size} bytes")
                
                return send_file(
                    downloaded_file,
                    as_attachment=True,
                    download_name=f"{video_id}.webm",
                    mimetype='audio/webm'
                )

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        logger.error(f"yt-dlp download error: {error_msg}")
        
        if 'Sign in to confirm' in error_msg:
            return jsonify({
                'error': 'YouTube bot detection triggered',
                'suggestion': 'Try again later or use a different method'
            }), 403
        elif 'Private video' in error_msg:
            return jsonify({'error': 'Video is private or unavailable'}), 404
        else:
            return jsonify({'error': f'Download failed: {error_msg}'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/info', methods=['POST'])
def get_info():
    """Get video info without downloading"""
    try:
        # Optional authentication
        if API_KEY and API_KEY != 'your-secret-key-123':
            if not authenticate(request):
                return jsonify({'error': 'Invalid API key'}), 401

        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL required in JSON body'}), 400

        url = data['url']
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'id': info.get('id'),
                'title': info.get('title'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'formats_available': len(info.get('formats', []))
            })

    except Exception as e:
        logger.error(f"Info extraction error: {str(e)}")
        return jsonify({'error': f'Failed to get info: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
