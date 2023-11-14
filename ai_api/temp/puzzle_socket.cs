using System.Net.Sockets;
using UnityEngine;
using System.IO;
using System;

public class SocketClient : MonoBehaviour
{
    private void Start()
    {
        SendImageToServer("path_to_your_image");
    }

    void SendImageToServer(string imagePath)
    {
        byte[] imageBytes = File.ReadAllBytes(imagePath);

        TcpClient client = new TcpClient("localhost", 12345);
        NetworkStream stream = client.GetStream();

        // 데이터 길이 전송
        byte[] dataLength = BitConverter.GetBytes(imageBytes.Length);
        stream.Write(dataLength, 0, 4);

        // 이미지 데이터 전송
        stream.Write(imageBytes, 0, imageBytes.Length);
        stream.Close();
        client.Close();
    }
}
