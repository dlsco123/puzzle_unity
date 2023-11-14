using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.IO;

public class TakePhoto : MonoBehaviour
{
    public RawImage photoDisplay;

    private Texture2D screenshot;
    private string fileName = "screenshot.png";
    private string uploadURL = "http://192.168.0.45:5001/main/upload-image";

    private void Start()
    {
        photoDisplay.texture = null;
        if (!Permission.HasUserAuthorizedPermission(Permission.ExternalStorageWrite))
        {
            Permission.RequestUserPermission(Permission.ExternalStorageWrite);
        }
    }

    public void CapturePhoto()
    {
        StartCoroutine(TakeScreenshot());
    }

    private IEnumerator TakeScreenshot()
    {
        yield return new WaitForEndOfFrame();

        RenderTexture currentRT = RenderTexture.active;
        RenderTexture renderTexture = RenderTexture.GetTemporary(
            photoDisplay.mainTexture.width,
            photoDisplay.mainTexture.height
        );
        RenderTexture.active = renderTexture;

        Graphics.Blit(photoDisplay.mainTexture, renderTexture);

        screenshot = new Texture2D(
            photoDisplay.mainTexture.width,
            photoDisplay.mainTexture.height
        );
        screenshot.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        screenshot.Apply();

        photoDisplay.texture = screenshot;

        RenderTexture.active = currentRT;
        RenderTexture.ReleaseTemporary(renderTexture);

        StartCoroutine(UploadDownloadCoroutine(screenshot));
    }

    private IEnumerator UploadDownloadCoroutine(Texture2D userImage)
    {
        byte[] imageBytes = userImage.EncodeToPNG();

        using (UnityWebRequest www = UnityWebRequest.Post(uploadURL, "POST"))
        {
            www.uploadHandler = new UploadHandlerRaw(imageBytes);
            www.uploadHandler.contentType = "image/png";
            www.downloadHandler = new DownloadHandlerBuffer();

            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError)
            {
                Debug.LogError(www.error);
            }
            else
            {
                Debug.Log("Image uploaded! Downloading FBX...");
                string fbxPath = Path.Combine(Application.persistentDataPath, "downloadedModel.fbx");
                File.WriteAllBytes(fbxPath, www.downloadHandler.data);
                Debug.Log($"FBX saved at: {fbxPath}");

                // 추가적으로 FBX 파일 로딩 및 활용하는 코드를 여기에 작성
            }
        }
    }
}
