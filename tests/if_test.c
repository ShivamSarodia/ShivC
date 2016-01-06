int main()
{
  int a = 3, b = 10, c = 15;

  if(a > 2)
    {
      if(b > a)
	{
	  int d = b + 1;
	  if(d > b) return 0;
	  return 4;
	}
      return 3;
    }
  return 1;

  
}
