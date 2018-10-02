#include <iostream>
using namespace std;

int main(){
  int nadia1 = 1;
  bool nadia2 = true;

  nadia1++;
  nadia1 = 9;

  if(nadia2) {
    nadia1--;
    nadia2 = false;
  }

  for(nadia1 = 0; nadia1 <= 5; nadia1++) {
    cout << nadia1 << endl;
  }

  if(nadia2){
    cout << "urrrmmm...";
  }

  return 0;
}
