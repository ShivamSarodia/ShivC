int fib_recursive(int n)
{
  if(n == 0) return 0;
  else if(n == 1) return 1;
  return fib_recursive(n-1) + fib_recursive(n-2);
}

int fib_iterative(int n)
{
  int f_this = 0;
  int f_next = 1;
  int temp;
  for(int i = 0; i < n; i++)
    {
      temp = f_next;
      f_next = f_this + f_next;
      f_this = temp;
    }
  return f_this;
}

/* -------------------------- */

int test_add(int a, int b)
{
  return a + b;
}

/* -------------------------- */

int array_sum(int* arr, int len)
{
  int sum = 0;
  for(int i = 0; i < len; i++)
    {
      arr[i] = (sum += arr[i]);
    }
  return 0;
}

/* -------------------------- */

int main()
{
  if( fib_recursive(30) != fib_iterative(30) ) return 1;

  /* ---------------------------------------- */
  
  for(int a = -10; a < 10; a++)
    {
      for(int b = -10; b < 10; b++)
	{
	  if(test_add(a, b) != a + b) return 2;
	}
    }

  /* ---------------------------------------- */

  int array[] = {1, 3, 5, 7, 9};
  array_sum(array, 5);
  if(array[4] != 25) return 3;

  /* ---------------------------------------- */
  
  return 0;
}
