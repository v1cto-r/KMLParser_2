from parser import parseKML

if __name__ == '__main__':
    plazas = parseKML("./DATA/SomeData.kml")
    secciones = parseKML("./DATA/OtherData.kml")

    for plaza in plazas:
        plaza.assignPolygon(secciones, "seccion")

    plazas.exportToExcel("new_plazas.xlsx")
