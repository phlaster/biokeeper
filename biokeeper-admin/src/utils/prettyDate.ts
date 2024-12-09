function getPrettyDateTime(input: Date | string): string {
    // Если input строка, преобразуем ее в объект Date
    const date = typeof input === 'string' ? new Date(input) : input;
  
    if (isNaN(date.getTime())) {
      // Если дата недействительна, возвращаем сообщение об ошибке
      return 'Invalid date';
    }
  
    const day = date.getDate();
    const month = date.getMonth() + 1; // Месяцы в JavaScript начинаются с 0
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = date.getMinutes();
  
    // Добавляем ведущие нули, если день, месяц, часы или минуты меньше 10
    const formattedDay = day < 10 ? `0${day}` : day;
    const formattedMonth = month < 10 ? `0${month}` : month;
    const formattedHours = hours < 10 ? `0${hours}` : hours;
    const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
  
    return `${formattedDay}.${formattedMonth}.${year} ${formattedHours}:${formattedMinutes}`;
  }

function getPrettyDate(input: Date | string): string {
  // Если input строка, преобразуем ее в объект Date
  const date = typeof input === 'string' ? new Date(input) : input;

  if (isNaN(date.getTime())) {
    // Если дата недействительна, возвращаем сообщение об ошибке
    return 'Invalid date';
  }

  const day = date.getDate();
  const month = date.getMonth() + 1; // Месяцы в JavaScript начинаются с 0
  const year = date.getFullYear();

  // Добавляем ведущие нули, если день, месяц, часы или минуты меньше 10
  const formattedDay = day < 10 ? `0${day}` : day;
  const formattedMonth = month < 10 ? `0${month}` : month;


  return `${formattedDay}.${formattedMonth}.${year}`;
}
  
export { getPrettyDate, getPrettyDateTime };
  