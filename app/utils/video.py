import magic
import mimetypes

def validate_video(stream):
	mime = magic.from_buffer(stream.read(512), mime=True)
	ext = mimetypes.guess_extension(mime)
	return ext