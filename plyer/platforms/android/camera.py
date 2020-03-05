import android
import android.activity
from os import remove
from jnius import autoclass, cast
from plyer.facades import Camera
from plyer.platforms.android import activity

Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.renpy.android.PythonActivity')
MediaStore = autoclass('android.provider.MediaStore')
Uri = autoclass('android.net.Uri')
FileProvider = autoclass('android.support.v4.content.FileProvider')
Context = autoclass("android.content.Context")
Environment = autoclass("android.os.Environment")

class AndroidCamera(Camera):
    def _take_picture(self, on_complete, filename=None):

        def create_img_file():
            File = autoclass('java.io.File')
            storageDir = Context.getExternalFilesDir(null)

            imageFile = File(
                storageDir,
                "gmv.jpg"
            )
            imageFile.createNewFile()

            return imageFile

        assert(on_complete is not None)
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self._on_activity_result)
        android.activity.bind(on_activity_result=self._on_activity_result)
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)

        photoFile = create_img_file()
        photoUri = FileProvider.getUriForFile(
            Context.getApplicationContext(),
            "org.test.myapp.fileprovider",
            photoFile
        )

        parcelable = cast('android.os.Parcelable', photoUri)

        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)
        activity.startActivityForResult(intent, 0x123)

    def _take_video(self, on_complete, filename=None):
        assert(on_complete is not None)
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self._on_activity_result)
        android.activity.bind(on_activity_result=self._on_activity_result)
        intent = Intent(MediaStore.ACTION_VIDEO_CAPTURE)
        uri = Uri.parse('file://' + filename)
        parcelable = cast('android.os.Parcelable', uri)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)

        # 0 = low quality, suitable for MMS messages,
        # 1 = high quality
        intent.putExtra(MediaStore.EXTRA_VIDEO_QUALITY, 1)
        activity.startActivityForResult(intent, 0x123)

    def _on_activity_result(self, requestCode, resultCode, intent):
        if requestCode != 0x123:
            return
        android.activity.unbind(on_activity_result=self._on_activity_result)
        if self.on_complete(self.filename):
            self._remove(self.filename)

    def _remove(self, fn):
        try:
            remove(fn)
        except OSError:
            pass


def instance():
    return AndroidCamera()
