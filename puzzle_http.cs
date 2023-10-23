using UnityEngine;
using UnityEngine.Networking;

IEnumerator UploadImage(Texture2D texture)
{
    byte[] imageBytes = texture.EncodeToPNG();
    WWWForm form = new WWWForm();
    form.AddBinaryData("image", imageBytes, "myImage.png", "image/png");

    using (UnityWebRequest www = UnityWebRequest.Post("http://your_fastapi_url/upload-image", form))
    {
        yield return www.SendWebRequest();
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Image uploaded!");
        }
    }
}
