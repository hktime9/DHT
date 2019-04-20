# DHT
A Python based Distributed Hash Table on a LocalHost
This p2p system takes the port as its input which it
uses as its unique key within the DHT. It then requires
you to enter the port of any existing node of the DHT
you want to join. If you want a seperate DHT, then you
can re-enter its own port. Other instances of the 
program are created in different directories and 
can be used to join this network. Once inside the network
you can upload files. Download files which are avaialble 
over the DHT. It knows when a node is down and can rejoin 
the remaining network. It uses finger tables to transfer files.
A classic implementation of the Chord decentralized system
