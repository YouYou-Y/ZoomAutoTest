import os, time, shutil, glob, logging, subprocess
from chat_bot import ChatBot, AlertLevel
from multiprocessing import Process
from shutil import copyfile

class AutoTest():

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    RunPath = 'C:/Users/daisy/PycharmProjects/ZoomAutoTest'
    ConfigPath = 'D:\Conformance\ConfigFile'
    SequencePath = 'D:\Conformance\TestSequences'
    DLL = '"D:\Conformance\TestSequences\zlt-anchor.dll" "D:\Conformance\TestSequences\zlt-perf.dll"'

    @staticmethod
    def post_message_to_chat_bot(group_id: str, header: str, msg, level=AlertLevel.info, logger=None):

        chat_bot = ChatBot(group_id, logger)
        return chat_bot.post_message(header, msg, level)

    def SendTestResult(self):

        self.post_message_to_chat_bot('3afe5f125ec24d7099bad92c291aeea7@conference.xmpp.zoom.us', 'Conformance Test', 'Test Result is: Failed', level=AlertLevel.error)
        #self.post_message_to_chat_bot('953b0d29ba414d4ab8c1316e56bd87d3@conference.xmpp.zoom.us', 'Conformance Test', 'Test Result is: Failed', level=AlertLevel.warning)

    def RunEncoderTestTool(self, TestSequence):

        ConfigFiles = glob.glob('{}\*.cfg'.format(AutoTest().ConfigPath))
        #logging.info("ConfigFiles: %s" % ConfigFiles)

        os.chdir(AutoTest().RunPath)

        flag = 1

        for index, item in enumerate(ConfigFiles):
            if flag == 1:
                ConfigFile = item
                #logging.info("ConfigFile: %s" % ConfigFile )

                ConfigFile1 = ConfigFile.rsplit('\\', 1)
                #logging.info("ConfigFile1: %s" % ConfigFile1)
                ConfigFile2 = ConfigFile1[-1]
                ConfigFileName = ConfigFile2.replace('"', "")
                logging.info("ConfigFileName: %s" % ConfigFileName)

                config = ConfigFileName[12:-4]
                #logging.info("config: %s" % config)

                testSequenceName1 = TestSequence.rsplit('\\', 1)
                testSequenceName = testSequenceName1[-1]
                #logging.info("TestSequence: %s" % TestSequence)
                #logging.info("testSequenceName: %s" % testSequenceName)
                sequenceName1 = testSequenceName.rsplit('.', 1)
                sequenceName = sequenceName1[0]
                logging.info("sequenceName: %s" % sequenceName)

                fileName = config + '+' + sequenceName
                #logging.info("fileName: %s" % fileName)

                srcTool = '{}/EncoderTestTool.exe'.format(AutoTest().RunPath)
                dstTool = '{0}/{1}/EncoderTestTool.exe'.format(AutoTest().RunPath, fileName)
                #logging.info("dstTool: %s" % dstTool)
                dstSequence = '{0}/{1}/{2}'.format(AutoTest().RunPath, fileName, testSequenceName)

                srcDLL = AutoTest().DLL.split()

                srcDLLAnchor1 = srcDLL[0]
                srcDLLAnchor = srcDLLAnchor1.replace('"', "")

                srcDLLPerf1 = srcDLL[1]
                srcDLLPerf = srcDLLPerf1.replace('"', "")

                #logging.info("srcDLLAnchor: %s" % srcDLLAnchor)
                #logging.info("srcDLLPerf: %s" % srcDLLPerf)

                dstDLLAnchor = '{0}/{1}/zlt-anchor.dll'.format(AutoTest().RunPath, fileName)
                dstDLLPerf = '{0}/{1}/zlt-perf.dll'.format(AutoTest().RunPath, fileName)

                #print(dstDLLAnchor)
                #print(dstDLLPerf)

                dstDLL = '"{0}" "{1}"'.format(dstDLLAnchor.replace('/', '\\'), dstDLLPerf.replace('/', '\\'))

                srcConfig = ConfigFile.replace('"', '')
                dstConfig = '{0}/{1}/{2}'.format(AutoTest().RunPath, fileName, ConfigFileName)

                if os.path.exists(fileName):
                    shutil.rmtree(fileName)
                    os.mkdir(fileName)
                else:
                    os.mkdir(fileName)

                copyfile(srcTool, dstTool)
                copyfile(TestSequence, dstSequence)
                copyfile(srcConfig, dstConfig)
                copyfile(srcDLLAnchor, dstDLLAnchor)
                copyfile(srcDLLPerf, dstDLLPerf)

                os.chdir('{0}/{1}'.format(AutoTest().RunPath, fileName)),
                #cmd = 'EncoderTestTool.exe -c {0} -s {1} -d {2} -p {3}'.format(ConfigFileName, TestSequence, DLL, ConfigFile)

                cmd = 'EncoderTestTool.exe -c {0} -s {1} -d {2} -p {3}'.format(ConfigFileName, testSequenceName, dstDLL, dstConfig)
                logging.info("Run cmd: %s" % cmd)

                process = subprocess.Popen(cmd, shell=True)
                pid = process.pid
                logging.info("Pid = %s" % pid)

                testresult = '{0}/{1}/EncoderTest-{1}.txt'.format(AutoTest().RunPath, fileName)
                time.sleep(50)
                os.path.exists(testresult)
                file = open(testresult)

                while 1:
                    where = file.tell()
                    line = file.readline()
                    if not line:
                        time.sleep(1)
                        file.seek(where)
                    else:
                        if 'pass' in line.lower():
                            time.sleep(1)
                            logging.info("%s: Test Result is Passed" % fileName)
                            os.system("taskkill /t /f /pid %s" % process.pid)
                            os.chdir(AutoTest().RunPath)
                            break
                        else:
                            if 'error' in line.lower():
                                logging.info("%s: Test Result is Failed" % fileName)
                                time.sleep(1)
                                AutoTest().SendTestResult()
                                time.sleep(1)
                                os.system("taskkill /t /f /pid %s" % process.pid)
                                os.chdir(AutoTest().RunPath)
                                flag = 0
                                break

if __name__ == '__main__':

    TestSequences = glob.glob('{}\*.yuv'.format(AutoTest().SequencePath))
    #logging.info("TestSequences: %s" % TestSequences)

    for index, sequence in enumerate(TestSequences):
        if index < 4:
            TestSequence = sequence
            autoTest = Process(target=AutoTest().RunEncoderTestTool, args=(TestSequence,))
            autoTest.start()