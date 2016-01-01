int main()
{
  int a = 3, b = 10, c = 15;

  if(a > 2)
    {
      if(b > a)
	{
	  int d = ++b;
	  if(++d > b)
	    {
	      int e = d - b - 1;
	      return e;
	    }
	  return 4;
	}
      return b;
    }
  return 1;
}
