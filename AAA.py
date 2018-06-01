import random
import hashlib, json, sys
import copy
import hashlib

import RPi.GPIO as GPIO 
import serial
import os, sys
import time

GPIO.setmode(GPIO.BOARD)                     
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count=0
ppm=0


def my_callback(channel):
    
    global count
    count=count+1
    
GPIO.add_event_detect(11, GPIO.FALLING, callback=my_callback) 
def counter():
        stamp1=count
        time.sleep(60)
        stamp2=count
        print ('pulses per minute')
        global ppm
        ppm = (abs(stamp1 - stamp2))
        ppm=round(ppm/3)
        print (ppm)

while True:
    try:
        
            ser = serial.Serial('/dev/ttyUSB0', 9600)
            ValorSensorph = ser.readline()
            ValorSensorph2 = ValorSensorph[:3]
            ValorSensorph3 = (int(ValorSensorph2))*5   
            ValorSensorph1  = ppm

           


            value = str(ValorSensorph3).encode()
            value1 = str(ValorSensorph1).encode()
            code = hashlib.sha256(value).hexdigest()
            code1 = hashlib.sha256(value1).hexdigest()

            
            print ("************************************")
            print ("Sensor BP: ", ValorSensorph3)
            print ("Sensor Heartrate:", ValorSensorph1)
            #print ("hash:", code)
            #print ("hash value:", code1)
            print ("************************************\n")

            

            

            def hashMe(ValorSensorph3=""):
               
                if type(ValorSensorph3)!=str:
                    ValorSensorph3 = json.dumps(ValorSensorph3,sort_keys=True)
                    
                    
                if sys.version_info.major == 2:
                    return unicode(hashlib.sha256(ValorSensorph3).hexdigest(),'utf-8')
                else:
                    return hashlib.sha256(str(ValorSensorph3).encode('utf-8')).hexdigest()
            random.seed(0)

            def makeTransaction(maxValue=3):
                ValorSensorph3     = int(random.getrandbits(1))*2 - 1
                ValorSensorph1  = random.randint(1,maxValue)
                alicePays = ValorSensorph3 * ValorSensorph1
                bobPays   = -1 * alicePays
                return {u'Alice':alicePays,u'Bob':bobPays}
            txnBuffer = [makeTransaction() for i in range(30)]

            def updateState(txn, state):
               
                state = state.copy() # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
                for key in txn:
                    if key in state.keys():
                        state[key] += txn[key]
                    else:
                        state[key] = txn[key]
                return state
            def isValidTxn(txn,state):

                if sum(txn.values()) is not 0:
                    return False
                for key in txn.keys():
                    if key in state.keys(): 
                        acctBalance = state[key]
                    else:
                        acctBalance = 0
                    if (acctBalance + txn[key]) < 0:
                        return False
                
                return True
            


            state = {u'Alice':ValorSensorph3, u'Bob':50}  # Define the initial state
            genesisBlockTxns = [state]
            genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txnCount':4,u'txns':genesisBlockTxns}
            genesisHash = hashMe( genesisBlockContents )
            genesisBlock = {u'hash':genesisHash,u'contents':genesisBlockContents}
            genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)
            chain = [genesisBlock]
            print('genesisHash ', genesisBlock)
            def makeBlock(txns,chain):
                parentBlock = chain[-1]
                parentHash  = parentBlock[u'hash']
                blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
                txnCount    = len(txns)
                blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,
                                 u'txnCount':len(txns),'txns':txns}
                blockHash = hashMe( blockContents )
                block = {u'hash':blockHash,u'contents':blockContents}
                print ('parentHash: ', parentHash)
                print('blockNumber: ',blockNumber)
                
                return block
            chain = [genesisBlock]
            blockSizeLimit = 5  
            while len(txnBuffer) > 0:
                bufferStartSize = len(txnBuffer)
                
                ## Gather a set of valid transactions for inclusion
                txnList = []
                while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
                    newTxn = txnBuffer.pop()
                    validTxn = isValidTxn(newTxn,state) # This will return False if txn is invalid
                    
                    if validTxn:           # If we got a valid state, not 'False'
                        txnList.append(newTxn)
                        state = updateState(newTxn,state)
                    else:
                        print("ignored transaction")
                        sys.stdout.flush()
                        continue  # This was an invalid transaction; ignore it and move on
                    
                ## Make a block
                myBlock = makeBlock(txnList,chain)
                chain.append(myBlock)
                chain[0]
                chain[1]
                
                state
                def checkBlockHash(block):
                # Raise an exception if the hash does not match the block contents
                    expectedHash = hashMe( block['contents'] )
                    if block['hash']!=expectedHash:
                        raise Exception('Hash does not match contents of block %s'%
                                        block['contents']['blockNumber'])
                    return
            def checkBlockValidity(block,parent,state):    
               
                parentNumber = parent['contents']['blockNumber']
                parentHash   = parent['hash']
                blockNumber  = block['contents']['blockNumber']
                
                # Check transaction validity; throw an error if an invalid transaction was found.
                for txn in block['contents']['txns']:
                    if isValidTxn(txn,state):
                        state = updateState(txn,state)
                    else:
                        raise Exception('Invalid transaction in block %s: %s'%(blockNumber,txn))

                checkBlockHash(block) # Check hash integrity; raises error if inaccurate

                if blockNumber!=(parentNumber+1):
                    raise Exception('Hash does not match contents of block %s'%blockNumber)

                if block['contents']['parentHash'] != parentHash:
                    raise Exception('Parent hash not accurate at block %s'%blockNumber)
                
                return state
            def checkChain(chain):
                
                if type(chain)==str:
                    try:
                        chain = json.loads(chain)
                        assert( type(chain)==list)
                    except:  # This is a catch-all, admittedly crude
                        return False
                elif type(chain)!=list:
                    return False
                
                state = {}
                
                for txn in chain[0]['contents']['txns']:
                    state = updateState(txn,state)
                checkBlockHash(chain[0])
                parent = chain[0]
                
               
                for block in chain[1:]:
                    state = checkBlockValidity(block,parent,state)
                    parent = block
                    
                return state

            checkChain(chain)
            chainAsText = json.dumps(chain,sort_keys=True)
            checkChain(chainAsText)
            nodeBchain = copy.copy(chain)
            nodeBtxns  = [makeTransaction() for i in range(5)]
            newBlock   = makeBlock(nodeBtxns,nodeBchain)
            print("Blockchain on Node A is currently %s blocks long"%len(chain))

            try:
                print("New Block Received; checking validity...")
                state = checkBlockValidity(newBlock,chain[-1],state) # Update the state- this will throw an error if the block is invalid!
                chain.append(newBlock)
            except:
                print("Invalid block; ignoring and waiting for the next block...")

            print("Blockchain on Node A is now %s blocks long"%len(chain))
            class Block(object):
                
                  def __init__(self, dictionary):
                    '''
                      We're looking for index, timestamp, data, prev_hash, nonce
                    '''
                    for k, v in dictionary.items():
                      setattr(self, k, v)

                    if not hasattr(self, 'nonce'):
                      #we're throwin this in for generation
                      self.nonce = 'None'
                    if not hasattr(self, 'hash'): #in creating the first block, needs to be removed in future
                      self.hash = (self.create_self_hash, 'utf-8')
                      
                  def header_string(self):
                    return str(self.index) + self.prev_hash + self.data + str(self.timestamp) + str(self.nonce)

                  def create_self_hash(self):
                    sha = hashlib.sha256()
                    sha.update(self.header_string, 'utf-8')
                    return sha.hexdigest()

                  def self_save(self):
                    chaindata_dir = 'chaindata'
                    index_string = str(self.index).zfill(6) #front of zeros so they stay in numerical order
                    filename = '%s/%s.json' % (chaindata_dir, index_string)
                    with open(filename, 'w') as block_file:
                      json.dump(self.__dict__(), block_file)

                  def __dict__(self):
                    info = {}
                    info['index'] = str(self.index)
                    info['timestamp'] = str(self.timestamp)
                    info['prev_hash'] = str(self.prev_hash)
                    info['hash'] = str(self.hash)
                    info['data'] = str(self.data)
                    info['nonce'] = str(self.nonce)
                    return info

                  def __str__(self):
                    return "Block<prev_hash: %s,hash: %s>" % (self.prev_hash, self.hash)

                def create_first_block():
                  # index zero and arbitrary previous hash
                  block_data = {}
                  block_data['index'] = 0
                  block_data['timestamp'] = date.datetime.now()
                  block_data['data'] = genesisHash 
                  block_data['prev_hash'] = 'genesisHash '
                  block_data['nonce'] = 0 #starting it at 0
                  return Block(block_data)

                if __name__ == '__main__':
                  #check if chaindata folder exists.
                  chaindata_dir = 'chaindata/'
                  if not os.path.exists(chaindata_dir):
                    #make chaindata dir
                    os.mkdir(chaindata_dir)
                  #check if dir is empty from just creation, or empty before
                  if os.listdir(chaindata_dir) == []:
                    #create and save first block
                    first_block = create_first_block()
                    first_block.self_save()

            counter()
  
    except KeyboardInterrupt:
        print ("\nSalida")
        break
