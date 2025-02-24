import gzip
import shutil
import traceback
import logging


def main():
    """Extractor de Gzips"""
    print('Bienvenivo al extractor de GZips')
    print()
    print('Favor ingresar ruta de archivo:')
    filepath = input().replace('"', '')
    print('Ruta ingresada:')
    print(filepath)
    print("Descomprimiendo...")
    try:
        with gzip.open(filepath, 'rb') as f_in:
            with open(filepath[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print('Descrompresion terminada!')
    except Exception as e:
        logging.exception(e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
