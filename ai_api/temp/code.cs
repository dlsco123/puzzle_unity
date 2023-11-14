using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using System.IO;
using ICSharpCode.SharpZipLib.Zip;

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
                Debug.Log("Image uploaded! Downloading ZIP...");

                string zipPath = Path.Combine(Application.persistentDataPath, "downloadedAssets.zip");
                File.WriteAllBytes(zipPath, www.downloadHandler.data);
                Debug.Log($"ZIP saved at: {zipPath}");

                ExtractZip(zipPath, Application.persistentDataPath);

                // 여기서 FBX 및 PNG 파일을 로드 및 활용
            }
        }
    }

    private void ExtractZip(string archivePath, string destinationPath)
    {
        try
        {
            using (ZipInputStream zipStream = new ZipInputStream(File.OpenRead(archivePath)))
            {
                ZipEntry entry;
                while ((entry = zipStream.GetNextEntry()) != null)
                {
                    string directoryName = Path.GetDirectoryName(entry.Name);
                    string fileName = Path.GetFileName(entry.Name);

                    if (directoryName.Length > 0)
                        Directory.CreateDirectory(Path.Combine(destinationPath, directoryName));

                    if (fileName != string.Empty)
                    {
                        using (FileStream streamWriter = File.Create(Path.Combine(destinationPath, entry.Name)))
                        {
                            int size = 2048;
                            byte[] data = new byte[2048];
                            while (true)
                            {
                                size = zipStream.Read(data, 0, data.Length);
                                if (size > 0)
                                    streamWriter.Write(data, 0, size);
                                else
                                    break;
                            }
                        }
                    }
                }
            }

            Debug.Log("ZIP file extracted!");
        }
        catch (System.Exception ex)
        {
            Debug.LogError("Error extracting zip file: " + ex.Message);
        }
    }
}
