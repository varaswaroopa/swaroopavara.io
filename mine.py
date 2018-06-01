from cryptography.fernet import Fernet
import random
import hashlib, json, sys
import copy
import hashlib
import datetime as date
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
            print ("hash:", code1)
            print ("************************************\n")
            SALT_SIZE = 16

            NUMBER_OF_ITERATIONS = 20
            AES_MULTIPLE = 16
            def generate_key(password, salt, iterations):
                assert iterations > 0

                key = password + salt

                for i in range(iterations):
                    key = hashlib.sha256(key).digest()  

                return key
            def encrypt(plaintext, password):
                salt = Crypto.Random.get_random_bytes(SALT_SIZE)

                key = generate_key(password, salt, NUMBER_OF_ITERATIONS)

                cipher = AES.new(key, AES.MODE_ECB)

                padded_plaintext = pad_text(plaintext, AES_MULTIPLE)

                ciphertext = cipher.encrypt(padded_plaintext)

                ciphertext_with_salt = salt + ciphertext

                return ciphertext_with_salt


           

            #key = '0de5f75970276a6579f29d824d5cef66c3a979b75048ce0704b57b301f966d8d'
            #iv = '175c741eda4f742c190706b104537ea0'

            



                 
            def hashMe(ValorSensorph1 ):
               
                if type(ValorSensorph1)!=str:
                    ValorSensorph1 = json.dumps(ValorSensorph1,sort_keys=True)
                    #print(ValorSensorph1)
                    
                    
                if sys.version_info.major == 2:
                    return unicode(hashlib.sha256(ValorSensorph1).hexdigest(),'utf-8')
                else:
                    return hashlib.sha256(str(ValorSensorph1).encode('utf-8')).hexdigest()
            random.seed(0)
            def new_wallet():
              random_gen = Crypto.Random.new().read
              private_key = RSA.generate(1024, random_gen)
              public_key = private_key.publickey()
              response = {
                'private_key': binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
                'public_key': binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
              }

            def makeTransaction(maxValue=3):
               
                alicePays = ValorSensorph3 * 10
                bobPays   = -1 * ValorSensorph1
                return {u'heartrate':alicePays,u'Bp':bobPays}
            txnBuffer = [makeTransaction() for i in range(30)]
           
             

            def updateState(txn, state):
               
                state = state.copy() 
                for key in txn:
                    if key in state.keys():
                        state[key] = txn[key]
                    else:
                        state[key] = txn[key]
                return state
            def isValidTxn(txn,state):

                if sum(txn.values()) is not 0:
                    return False
                for key in txn.keys():
                    if key in state.keys(): 
                       ValorSensorph1 = state[key]
                    else:
                        ValorSensorph1 = 0
                        ValorSensorph3 = 0
                    if (txn[key]) < 0:
                        return False
                
                return True
            
            state = {u'heartrate':ValorSensorph3, u'Bp':ValorSensorph1} 
            genesisBlockTxns = [state]
            genesisBlockContents = {u'blockNumber':0,u'parentHash':None,u'txns':genesisBlockTxns}
            genesisHash = hashMe( genesisBlockContents )
            genesisBlock = {u'hash':genesisHash ,u'contents':genesisBlockContents}
            
            genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)
            chain = [genesisBlock]
            print('genesisHash ',genesisHash)
            def makeBlock(txns,chain):
                parentBlock = chain[-1]
                parentHash  = parentBlock[u'hash']
                blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
                txnCount    = len(txns)
                blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,
                                 u'txnCount':len(txns),u'txns':txns}
                blockHash = hashMe( blockContents )
                block = {u'hash':blockHash,u'contents':blockContents}
                print ('parentHash: ', parentHash)
                print('blockNumber: ', blockNumber)
                
                
                return block
            chain = [genesisBlock]
            blockSizeLimit = 6  
            while len(txnBuffer) > 0:
                bufferStartSize = len(txnBuffer)
                
                
                txnList = []
                while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
                    newTxn = txnBuffer.pop()
                    validTxn = isValidTxn(newTxn,state)
                    
                    if validTxn:          
                        txnList.append(newTxn)
                        state = updateState(newTxn,state)
                    else:
                        #print("ignored transaction")
                        sys.stdout.flush()
                        continue  
                myBlock = makeBlock(txnList,chain)
                chain.append(myBlock)
                
                
                state
                def checkBlockHash(block):
               
                    expectedHash = hashMe( block['contents'] )
                    if block['hash']!=expectedHash:
                        raise Exception('Hash does not match contents of block %s'%
                                        block['contents']['blockNumber'])
                    return
            def checkBlockValidity(block,parent,state):    
               
                parentNumber = parent['contents']['blockNumber']
                parentHash   = parent['hash']
                blockNumber  = block['contents']['blockNumber']
                
                
                for txn in block['contents']['txns']:
                    if isValidTxn(txn,state):
                        state = updateState(txn,state)
                    else:
                        raise Exception('Invalid transaction in block %s: %s'%(blockNumber,txn))

                checkBlockHash(block) 

                if blockNumber!=(parentNumber+1):
                    raise Exception('Hash does not match contents of block %s'%blockNumber)

                if block['contents']['parentHash'] != parentHash:
                    raise Exception('Parent hash not accurate at block %s'%blockNumber)
                
                return state
            def mine():
           
                last_block = blockchain.chain[-1]
                blockchain.submit_transaction(sender_address=MINING_SENDER, recipient_address=blockchain.node_id, value=MINING_REWARD, signature="")

           
                previousHash = blockchain.hash(last_block)
                block = blockchain.create_block(nonce, previous_hash)
                prev_block = node_blocks[-1]
                new_block = mine(prev_block)
                new_block.self_save()

                response = {
                    'message': parentHash  ,
                    'blocknumber': block[blockNumber],
                    'transactions': block[txn],
                    'nonce': block[nonce],
                    'previousHash': block[previousHash],
                }
               
                return jsonify(response), 200
            def checkChain(chain):
                
                if type(chain)==str:
                    try:
                        chain = json.loads(chain)
                        assert( type(chain)==list)
                    except:  
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
            def decrypt(ciphertext, password):
                salt = ciphertext[0:SALT_SIZE]

                ciphertext_sans_salt = ciphertext[SALT_SIZE:]

                key = generate_key(password, salt, NUMBER_OF_ITERATIONS)

                cipher = AES.new(key, AES.MODE_ECB)

                padded_plaintext = cipher.decrypt(ciphertext_sans_salt)

                plaintext = unpad_text(padded_plaintext)

                return plaintext

           
            class Block(object):
              def __init__(present, dictionary):
                '''
                  We're looking for index, timestamp, data, prev_hash, nonce
                '''
                for k, v in dictionary.items():
                  setattr(present, k, v)

                if not hasattr(present, 'nonce'):
                  
                  present.nonce = chain
                
                  
              def header_string(present):
                return str(present.index) + present.prev_hash + present.data + str(present.timestamp) + str(present.nonce)

              def auto_save(present):
                chaindata_dir = 'Genesisdata'
                index_string = str(present.index).zfill(6) 
                filename = '%s/%s.json' % (chaindata_dir, index_string)
               
                with open(filename, 'w') as block_file:
                  json.dump(present.__dict__(), block_file)
              
                

              def __dict__(present):
                info = {}
                info['index'] = str(present.index)
                info['timestamp'] = str(present.timestamp)
                info['prev_hash'] = str(present.prev_hash)
                
                info['data'] = str(present.data)
                info['nonce'] = str(present.nonce)
                return info

              def __str__(present):
                return "Block<prevhash: %s,hash: %s>" % (present.prevhash, present.hash)

            def first_block():
              
              block_data = {}
              block_data['index'] = 0
              block_data['timestamp'] = date.datetime.now()
              block_data['data'] =  genesisHash
              block_data['prev_hash'] = genesisHash 
              block_data['nonce'] = 0 
              return Block(block_data)

            if __name__ == '__main__':
              
              chaindata_dir = 'Genesisdata/'
              if not os.path.exists(chaindata_dir):
                
                os.mkdir(chaindata_dir)
             
              if os.listdir(chaindata_dir) == []:
                
                first_block = first_block()
                first_block.auto_save()
            
                    
            counter()   
    except KeyboardInterrupt:
        print ("\nSalida")
        break
