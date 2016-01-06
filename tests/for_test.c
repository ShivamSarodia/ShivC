int main()
{
  int sum = 0;
  for(int i = 0; i < 10; i++)
    {
      sum += i;
    }

  if(sum != 45) return 1;

  /* ------------------------------ */
  
  sum = 0;
  for(int j = 0; j < 10; j++) sum += j;

  if(sum != 45) return 2;

  /* ------------------------------ */

  int k = 0;
  sum = 0;
  for(; k < 10;)
    {
      int m = sum + k;
      sum = m;
      k++;
    }

  if(sum != 45) return 3;

  /* ------------------------------ */

  for(int l; l < 10; l++);
  for(int l; l < 10; l++){}

  /* ------------------------------ */

  int i_sum = 0;
  for(int i = 0; 1; i++)
    {
      if(i == 10) break;
      else if(i == 5)
	{
	  continue;
	}

      i_sum += i;
    }

  if(i_sum != 40) return 4;

  /* ------------------------------ */
    
  int i, j, m; /* making sure i, j, m above are in correct scope */

  return 0;
}
