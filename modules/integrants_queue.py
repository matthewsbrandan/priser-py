def get_ministers_queue(weekdays, ministers, scales):
  availableMinistersToWeekday = {}
  scalesOnAvailableDays = {}
  ministersQueue = {}
  for weekday in weekdays:
    scalesOnAvailableDays[weekday] = list(filter(lambda scale: weekday in scale['weekday'], scales))
    for minister in filter(lambda scale: 'ministro' in scale['ability'].split(','), scalesOnAvailableDays[weekday]):
      if(weekday in ministersQueue):
        if(not minister['nickname'] in ministersQueue[weekday]):
          ministersQueue[weekday].append(minister['nickname'])
      else:
        ministersQueue[weekday] = [minister['nickname']]
    
    availableMinistersToWeekday[weekday] = list(
      map(lambda minister: minister['nickname'], filter(lambda minister: weekday in minister['availability'].split(','), ministers))
    )
    for available in availableMinistersToWeekday[weekday]:
      if(weekday in ministersQueue):
        if(not available in ministersQueue[weekday]):
          ministersQueue[weekday].append(available)
      else:
        ministersQueue[weekday] = [available]
  return ministersQueue