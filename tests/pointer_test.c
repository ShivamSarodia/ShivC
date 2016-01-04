int main()
{
  int a = 5, *a_p = &a;

  int *a_pold = a_p;
  
  a_p++;
  a_p--;
  ++a_p;
  --a_p;

  if ( a_pold - a_p != 0 ) return 1;

  a_p = a_p + 1;
  a_p += 1;

  if ( a_p - a_pold != 2 ) return 2;

  a_p = a_p - 1;
  a_p -= 1;

  if ( a_pold - a_p != 0 ) return 3;

  (*a_p)++;
  ++(*a_p);

  if (a != 7) return 4;

  (*a_p) += 3;
  (*a_p) -= 3;

  if (a != 7) return 5;
  
  --(*a_p);
  (*a_p)--;

  if (a != 5) return 6;
  
  if( a - *a_p != 0) return 7;

  int b = 10, *b_p = &b, **b_pp = &b_p;
  if (b - **b_pp != 0) return 8;
  
  int c = 10;
  if ( c - *&c != 0 ) return 9;

  return 0;
}
