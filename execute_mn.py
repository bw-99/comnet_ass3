net.pingFull([receiver,sender])
net.iperf([receiver,sender],seconds=5)

popens = {}
popens[receiver] = receiver.popen('python','receiver.py')
popens[sender] = sender.popen('python','sender.py',recvAddr, str(windowSize), srcFilename, dstFilename)