#include <iostream>
using namespace std;

int main(){
    int n;
    int t1 = 1;
    int t2 = 1;
    cout << "Fibonacci Series: ";

    //choose the largest value of the sequence here:
    n = 8;

    int nextTerm = 0;
    for(int i = 1; i <= n; ++i){
        // Prints the first two terms.
        if(i == 1){
            cout << t1 << " ";
            continue;
        }
        if(i == 2){
            cout << t2 << " ";
            continue;
        }

        nextTerm = t1 + t2;
        t1 = t2;
        t2 = nextTerm;

        cout << nextTerm << " ";
    }
    return 0;
}
