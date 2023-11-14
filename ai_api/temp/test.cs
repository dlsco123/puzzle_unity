// 필요한 네임스페이스
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System.IO;

// 응답을 위한 클래스 정의
[System.Serializable]
public class ApiResponse
{
    public string url;
}




// 이미지 업로드 및 다운로드 관리 클래스
public class ImageUploaderAndDownloader : MonoBehaviour
{
    public string fastApiUploadUrl = "http://yourfastapiaddress.com/upload-image";
    public Texture2D imageToUpload;
    public int size = 2; // 예: 2, 3 또는 4

    public void StartUploadImage()
    {
        StartCoroutine(UploadImageCoroutine());
    }

    private IEnumerator UploadImageCoroutine()
    {
        byte[] imageData = imageToUpload.EncodeToPNG();

        WWWForm form = new WWWForm();
        form.AddField("size", size);
        form.AddBinaryData("file", imageData, "image.png", "image/png");

        using (UnityWebRequest webRequest = UnityWebRequest.Post(fastApiUploadUrl, form))
        {
            yield return webRequest.SendWebRequest();

            if (webRequest.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Error: " + webRequest.error);
            }
            else
            {
                string responseText = webRequest.downloadHandler.text;
                string fileUrl = GetUrlFromResponse(responseText);

                StartCoroutine(DownloadFileCoroutine(fileUrl));
            }
        }
    }

    private string GetUrlFromResponse(string response)
    {
        ApiResponse responseObj = JsonUtility.FromJson<ApiResponse>(response);
        return responseObj.url;
    }

    private IEnumerator DownloadFileCoroutine(string url)
    {
        using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
        {
            yield return webRequest.SendWebRequest();

            if (webRequest.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Download failed: " + webRequest.error);
            }
            else
            {
                byte[] fileData = webRequest.downloadHandler.data;
                SaveToFile("YourLocalPath/file.zip", fileData);
            }
        }
    }

    private void SaveToFile(string path, byte[] data)
    {
        File.WriteAllBytes(path, data);
        Debug.Log("Saved to " + path);
    }
}
