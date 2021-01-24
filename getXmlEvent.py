import re 
eventList = re.findall('(?P<Event>Id[\s\S]*?)Id\s',txt)
print(eventList[0])

for event in eventList:
  id = re.findall('Id          : (?P<EventId>\d+)',event)
  template = re.findall('<data name="(?P<DataName>.*?)"\sinType="(?P<InType>.*?)"\soutType="(?P<OutType>.*?)"',event)
  description = re.findall('Description : (?P<Description>[\s\S]*)',event)
  descriptionEvent = re.sub('\\n','',description[0])
  descriptionEvent = re.sub('              ',' ',descriptionEvent)
  descriptionEvent = re.sub('   ',' ',descriptionEvent)
  descriptionEvent = re.sub('  ',' ',descriptionEvent)
  descriptionEvent = re.sub(':\s+',': ',descriptionEvent)
  descriptionList = re.split('\\n',description[0])
  header = ''
  headerFlag = False
  result = []
  # =========================
  for tmp in descriptionList:
    print("=> "+tmp)
    if headerFlag:
      header = re.findall('\s+(.*):\s+\%(\d)',tmp)
      headerFlag = False
      if header:
        result.append((header[0][1],header[0][0].replace(' ','')))
        header = ''
      else:
        header = re.findall('\s+(.*):',tmp)
        header = header[0].replace(' ','') 
      continue;
    if("              " == tmp):
      headerFlag = True
      continue;

    if re.findall('\:',tmp):
      subname = re.findall('\s+(.*):\s+\%(\d)',tmp)
      result.append((subname[0][1],header+subname[0][0].replace(' ','')))
  result = dict(result)
  mapping = []
  position = 0
  for index in range(len(template)): 
    mapping.append((result[str(index+1)],template[index][0],template[index][1:]))

  print(mapping)
