from kerykeion import AstrologicalSubject, KerykeionChartSVG



def svg_string_to_png(svg_string, output_path=None, scale=1, background_color=None):
        """
        Converts an SVG string to a PNG image.

        Args:
            svg_string: The SVG string to convert.
            output_path: The path to save the PNG image. If None, returns a BytesIO object.
            scale: Scaling factor for the output image.
            background_color: Background color for the image (e.g., "white", "#FFFFFF", "rgb(255, 255, 255)").
        Returns:
            If output_path is None, returns a BytesIO object containing the PNG data.
            Otherwise, saves the PNG to output_path and returns None.
        """
        png_data = svg2png(
            bytestring=svg_string.encode('utf-8'),
            scale=scale,
            background_color=background_color
        )
        
        if output_path:
            with open(output_path, "wb") as f:
                f.write(png_data)
            return None
        else:
             return BytesIO(png_data)


        
def main():
    bho = AstrologicalSubject(
        "bho", 1988, 3, 18, 6, 20,
        lng=-74.063644,
        lat=4.624335,
        tz_str="America/Bogota",
        city="Bogota"
    )
    svg_path = "bho - Natal Chart.svg"
    birth_chart_svg = KerykeionChartSVG(bho)
    birth_chart_svg.makeSVG()
    #help(birth_chart_svg)
    
    print(f"Birth chart SVG saved as '{svg_path}'.")



if __name__ == "__main__":
    main()