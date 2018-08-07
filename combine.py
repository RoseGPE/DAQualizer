import csv

carTimeField = 'time'
ecuTimeField = 'Time (sec)'

def getLine(d):
    try:
        return next(d)
    except StopIteration:
        None


def combine(daqfile_name, ecufile_name, mergefile_name, offset):
    with open(daqfile_name) as carlog:
        with open(ecufile_name) as eculog:
            with open(mergefile_name, 'w', newline='') as output:
                carlogReader = csv.DictReader(carlog)
                eculogReader = csv.DictReader(eculog)
                fieldnames = eculogReader.fieldnames + carlogReader.fieldnames[1:]
                merged = csv.DictWriter(output, fieldnames)
                merged.writeheader()

                print(fieldnames)
                carline = getLine(carlogReader)
                eculine = getLine(eculogReader)
                while True:
                    row = {}
                    
                    if(carline is None and eculine is None):
                        break
                    elif(carline is not None and eculine is None):
                        time = carline.pop(carTimeField)
                        if(float(time) > 1000.0):
                            row[ecuTimeField] = time
                            row = {**row, **carline}
                        carline = getLine(carlogReader)
                    elif(eculine is not None and carline is None):
                        time = eculine[ecuTimeField]
                        if(float(time) > 1000.0):
                            row = {**eculine}
                        eculine = getLine(eculogReader)
                    else:
                        carTime = float(carline[carTimeField])
                        ecuTime = round(float(eculine[ecuTimeField]) + float(args.offset), 3)
                        if(carTime < ecuTime):
                            if(carTime > 1000.0):
                                row[ecuTimeField] = carline.pop(carTimeField)
                                row = {**row, **carline}
                            carline = getLine(carlogReader)
                        elif(carTime == ecuTime):
                            if(carTime > 1000.0):
                                carline.pop(carTimeField)
                                eculine.pop(ecuTimeField)
                                row[ecuTimeField] = str(carTime)
                                row = {**row, **eculine, **carline}
                            carline = getLine(carlogReader)
                            eculine = getLine(eculogReader)
                        elif(carTime > ecuTime):
                            if(carTime > 1000.0):
                                eculine.pop(ecuTimeField)
                                row[ecuTimeField] = str(ecuTime)
                                row = {**row, **eculine}
                            eculine = getLine(eculogReader)
                    # if(ecuTimeField not in row):
                    #     print('{} {}'.format(carTime, ecuTime))
                    merged.writerow(row)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("carlog", help="path to first file")
    parser.add_argument("eculog", help="path to second file")
    parser.add_argument("mergelog", help="path to merged file")
    parser.add_argument("offset", help="offset for second file time series")
    args = parser.parse_args()

    combine(args.carlog, args.eculog, args.mergelog, args.offset)