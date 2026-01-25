agoras-media
============

Image and video processing for social media platforms.

Installation
------------

.. code-block:: bash

   pip install agoras-media

Contents
--------

- **MediaFactory**: Factory for creating Image and Video instances
- **Image**: Image download, validation, and processing
- **Video**: Video download, validation, and platform-specific limits

Usage
-----

.. code-block:: python

   import asyncio
   from agoras.media import MediaFactory, Image, Video

   # Create and download images
   async def download_image():
       image = Image('https://example.com/image.jpg')
       await image.download()
       # Use image.content, image.temp_file
       image.cleanup()

   # Create platform-specific video
   async def download_video():
       video = MediaFactory.create_video('https://example.com/video.mp4', 'facebook')
       await video.download()
       # Use video.content, video.temp_file
       video.cleanup()

   # Download multiple images
   async def batch_download():
       images = await MediaFactory.download_images([
           'https://example.com/image1.jpg',
           'https://example.com/image2.jpg'
       ])
       for img in images:
           print(f'Downloaded: {img.url}')
           img.cleanup()

   asyncio.run(download_image())

Dependencies
------------

- agoras-common
- Pillow (image processing)
- filetype (file type detection)
