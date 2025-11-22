"""
Audio processor using OpenAI Whisper for speech-to-text.
Converts audio files to text with timestamps for citations.
"""

import whisper
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Process audio files and convert to text using Whisper."""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize the audio processor.
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"AudioProcessor initialized with model: {model_name}")
    
    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
    
    def transcribe(self, file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            file_path: Path to the audio file
            language: Language code (optional, auto-detect if None)
            
        Returns:
            Dictionary containing transcript and metadata
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            # Load model if not already loaded
            self.load_model()
            
            # Transcribe
            logger.info(f"Transcribing audio file: {path.name}")
            
            options = {}
            if language:
                options['language'] = language
            
            result = self.model.transcribe(str(file_path), **options)
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get('segments', []):
                segments.append({
                    'id': segment['id'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'timestamp': f"{self._format_timestamp(segment['start'])} - {self._format_timestamp(segment['end'])}"
                })
            
            # Metadata
            metadata = {
                'language': result.get('language', 'unknown'),
                'duration': segments[-1]['end'] if segments else 0,
                'num_segments': len(segments),
            }
            
            logger.info(f"Transcription complete: {len(segments)} segments, language: {metadata['language']}")
            
            return {
                'text': result['text'].strip(),
                'segments': segments,
                'metadata': metadata,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio {file_path}: {str(e)}")
            return {
                'text': '',
                'segments': [],
                'metadata': {},
                'success': False,
                'error': str(e)
            }
    
    def transcribe_segment(self, file_path: str, start_time: float, end_time: float) -> str:
        """
        Transcribe a specific segment of audio.
        
        Args:
            file_path: Path to the audio file
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Transcribed text for the segment
        """
        try:
            # For segment transcription, you would typically use audio processing
            # libraries like pydub to extract the segment first
            # This is a simplified version
            
            result = self.transcribe(file_path)
            
            if not result['success']:
                return ""
            
            # Find segments within the time range
            segment_texts = []
            for segment in result['segments']:
                if segment['start'] >= start_time and segment['end'] <= end_time:
                    segment_texts.append(segment['text'])
            
            return ' '.join(segment_texts)
            
        except Exception as e:
            logger.error(f"Error transcribing segment: {str(e)}")
            return ""
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds to MM:SS or HH:MM:SS format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_segment_at_time(self, segments: List[Dict[str, Any]], timestamp: float) -> Optional[Dict[str, Any]]:
        """
        Get the segment that contains a specific timestamp.
        
        Args:
            segments: List of transcript segments
            timestamp: Time in seconds
            
        Returns:
            Segment dictionary or None
        """
        for segment in segments:
            if segment['start'] <= timestamp <= segment['end']:
                return segment
        return None
