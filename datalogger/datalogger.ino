#include <FlexCAN.h>
#include "SdFat.h"

#define FILE_BASE_NAME "log"

SdFatSdioEX sd;
SdFile file;

const uint8_t BASE_NAME_SIZE = sizeof(FILE_BASE_NAME) - 1;
char fileName[13] = FILE_BASE_NAME "00.tsv";

bool logging = false;

void openFile() {
  while (sd.exists(fileName)) {
    if (fileName[BASE_NAME_SIZE + 1] != '9') {
      fileName[BASE_NAME_SIZE + 1]++;
    } else if (fileName[BASE_NAME_SIZE] != '9') {
      fileName[BASE_NAME_SIZE + 1] = '0';
      fileName[BASE_NAME_SIZE]++;
    } else {
      Serial.println("Can't create file name");
    }
  }
  if (!file.open(fileName, O_CREAT | O_WRITE | O_EXCL)) {
    Serial.println("file.open");
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(1000);
  Serial.println("DAQ Started");

  Can0.begin(1E6);
  sd.begin();
  //  openFile();
}

void loop() {
  // put your main code here, to run repeatedly:
  static uint16_t count;
  CAN_message_t msg;
  if (Can0.read(msg))
  {
    count++;
    //    Serial.printf("logging: %03x\n", msg.id);
    if (msg.id == 0x500 && ((msg.buf[0] & 0x0F) == 4) && (!logging))
    {
      Serial.println("Logging");
      logging = true;
      if (file.isOpen())
        file.close();
      openFile();
    }
    else if (msg.id == 0x500 && ((msg.buf[0] & 0x0F) != 4) && (logging))
    {
      Serial.println("Done");
      logging = false;
      if (file.isOpen())
        file.close();
    }
    if (logging) {
      file.printf("%03x\t", msg.id);
      for (int i = 0; i < msg.len; i++)
        file.printf("%02x\t", msg.buf[i]);
      file.println();
      if (count % 10 == 0)
      {
        if (!file.sync() || file.getWriteError()) {
          Serial.println("write error");
        }
        if (file.fileSize() > 2E9 && file.isOpen())
        {
            file.close();
            openFile();
        }
      }
    }
  }
}
