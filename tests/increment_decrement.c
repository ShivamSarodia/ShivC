int main()
{
  int a = 10, b = 15;

  a++;
  --a;
  ++a;
  a--;
  
  b -= ++a + 3; /* a = 11, b = 1 */
  b = a - b; /* b = 10 */
  b--; /* b = 9 */
  b = b - 9; /* b = 0 */
    
  return b;
}
