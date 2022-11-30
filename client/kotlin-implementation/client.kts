import java.io.OutputStream
import java.net.Socket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.DatagramPacket
import java.net.InetSocketAddress
import java.nio.charset.Charset
import java.util.*
import kotlin.concurrent.thread

main()

fun main() {
    val clientToRendezvousServer = UdpClient("0.0.0.0", 50001)
    clientToRendezvousServer.sendPacket("0", "34.125.197.205", 55555)
    var isRead = false
    while (!isRead) {
        val data = clientToRendezvousServer.recv(1024)
        if (data == "ready") {
            isRead = true
        }
        val routeData = data.split(' ')
        if (routeData.size == 3) {
            val ip = routeData[0]
            val sport = routeData[1].toInt()
            var dport = String(routeData[2].toByteArray().filter { it > 0 }.toByteArray()).toInt()
            clientToRendezvousServer.close()

            //Punch hole to peer
            val clientHolePunch = UdpClient("0.0.0.0", sport)
            clientHolePunch.sendPacket("0", ip, dport)
            clientHolePunch.close()

            //Message exchange
            fun messageListen() {
                val clientListen = UdpClient("0.0.0.0", sport)
                while (true) {
                    val receivedMessage = clientListen.recv(1024)
                    println(receivedMessage)
                }
                clientListen.close()
            }
            thread {
                messageListen()
            }

            val clientSendMessage = UdpClient("0.0.0.0", dport)
            clientSendMessage.sendPacket("msg", ip, sport)
            clientSendMessage.close()
        }
    }
}


class UdpClient(address: String, port: Int) {
    private val _connection: DatagramSocket
    private val _address: InetAddress
    private val _port: Int

    init {
        _port = port
        _address = InetAddress.getByName(address);
        _connection = DatagramSocket(port, _address)
    }

    fun sendPacket(str: String, destinationAddress: String, destinationPort: Int) {
        val _destinationAddress = InetAddress.getByName(destinationAddress);
        val packet = DatagramPacket(str.toByteArray(), str.length, _destinationAddress, destinationPort);
        _connection.send(packet)
    }

    fun recv(bufferSize: Int): String {
        val buffer = ByteArray(bufferSize)
        val packet = DatagramPacket(buffer, buffer.size)
        _connection.receive(packet)
        return packet.data.decodeToString()
    }

    fun close() {
        _connection.close()
    }
}