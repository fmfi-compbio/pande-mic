import os
import argparse

def fake_debarcoder(inp, out, n):
    if not os.path.exists(out):
        os.mkdir(out)
    files = os.listdir(inp)
    
    for i in range(1,n+1):
        barcode = ""
        if i<=9:
            barcode = "run00"+str(i)
        elif i<=100:
            barcode = "run0"+str(i)
        barcode_path = os.path.join(out,barcode)
        os.system("mkdir "+barcode_path)
            
    
    #print(files)
    for f in files:
        if len(f)>=6 and f[0]!=".":
            barcode = f[:6]
            barcode_path = os.path.join(out,barcode)
            from_path = os.path.join(inp, f)
            to_path = os.path.join(barcode_path, f)
            os.system("cp "+from_path+" "+to_path)
            
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help = "input dir")
    parser.add_argument("-o", "--output", help = "output dir")
    parser.add_argument("-n", "--num_barcodes", help="num of barcodes")
    
    args = parser.parse_args()
    
    inp = args.input
    out = args.output
    n = int(args.num_barcodes)
    
    fake_debarcoder(inp, out, n)

if __name__ == "__main__":
    main()
