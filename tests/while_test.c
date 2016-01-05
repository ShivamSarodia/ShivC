int main()
{
  int i = 2;
  int counter = 0;
  
  while(i < 100)
    {
      counter++;
      
      if(counter == 2)
	{
	  continue;
	}

      int i2 = i;
      i = i + i2;
    }

  if(i != 128) return 1;
  if(counter != 7) return 2;
  
  /* ------------------------------------- */

  int j = 0;
  while(1) if(++j == 15) break;
  if(j != 15) return 3;

  /* --------------------------------------- */

  int index = 0;
  int odd_numbers[20];
  while(index < 20)
    {
      odd_numbers[index] = 2*index+1;
      index++;
    }
  
  int index2 = 0;
  int sum = 0;
  while(index2 < 20)
    {
      sum += odd_numbers[index2];
      index2++;

      if(sum != index2*index2) return 4;
    }

  if(index2 != 20) return 5;
  /* ------------------------------------ */

  return 0;
}
