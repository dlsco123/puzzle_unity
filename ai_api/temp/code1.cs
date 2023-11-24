using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using ICSharpCode.SharpZipLib.Zip;
using System.IO;

public class UpLoadManager : MonoBehaviour
{
    private string uploadURL = "http://192.168.0.44:5001/main/upload-image";
    private string fbxPath; // ZIP 파일 저장 경로
    private int maxCount; // 최대 플레이어 수

    private void Start()
    {
        maxCount = LobbyManager.instance.maxPlayers; // 최대 플레이어 수 초기화
    }

    public void UploadAndDownloadFBX(Texture2D userImage, int size)
    {
        StartCoroutine(UploadDownloadCoroutine(userImage, size));
    }

    private IEnumerator UploadDownloadCoroutine(Texture2D userImage, int size)
    {
        yield return StartCoroutine(UploadImageCoroutine(userImage, size));
    }

    private IEnumerator UploadImageCoroutine(Texture2D userImage, int size)
    {
        byte[] imageBytes = userImage.EncodeToPNG();
        WWWForm form = new WWWForm();
        form.AddBinaryData("file", imageBytes);
        form.AddField("size", size); // size 매개변수

        using (UnityWebRequest www = UnityWebRequest.Post(uploadURL, form))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Image uploaded successfully!");
                string fileURL = www.downloadHandler.text; // 서버로부터 파일의 URL을 받음
                StartCoroutine(DownloadZipCoroutine(fileURL));
            }
            else
            {
                Debug.LogError("Image upload failed: " + www.error);
            }
        }
    }

    private IEnumerator DownloadZipCoroutine(string fileURL)
    {
        fbxPath = Path.Combine(Application.persistentDataPath, "downloaded.zip"); // ZIP 파일 경로 설정

        using (UnityWebRequest www = UnityWebRequest.Get(fileURL))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("ZIP downloaded successfully!");
                File.WriteAllBytes(fbxPath, www.downloadHandler.data);
                ExtractZip(fbxPath, Application.persistentDataPath);
            }
            else
            {
                Debug.LogError("ZIP download failed: " + www.error);
            }
        }
    }

    private void ExtractZip(string archivePath, string destinationPath)
    {
        try
        {
            using (ZipFile zip = new ZipFile(File.OpenRead(archivePath)))
            {
                foreach (ZipEntry entry in zip)
                {
                    if (!entry.IsFile)
                        continue;

                    string filePath = Path.Combine(destinationPath, entry.Name);
                    if (!Directory.Exists(Path.GetDirectoryName(filePath)))
                        Directory.CreateDirectory(Path.GetDirectoryName(filePath));
                    
                    using (var stream = zip.GetInputStream(entry))
                    using (FileStream fileStream = File.Create(filePath))
                    {
                        stream.CopyTo(fileStream);
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
