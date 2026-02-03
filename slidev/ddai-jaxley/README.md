
From the `.potx`:
```sh
unzip cmu-powerpoint-digitaltartan.potx -d potx
# convert emf to svg
inkscape potx/ppt/media/image3.emf --export-type=svg -o potx/ppt/media/image3.svg

# format xml files for readability while reverse-engineering
# find . -name '*.xml' -type f -print0 | while IFS= read -r -d '' f; do
#   xmllint --format "$f" > "$f.fmt" && mv "$f.fmt" "$f"
# done

# cp and rename
cp potx/ppt/media/{image1.png, image2.png, image3.svg} assets/
mv ./assets/image1.png ./assets/plaid-square.png
mv ./assets/image2.png ./assets/cmu-square-red-trans.png
mv ./assets/image3.svg ./assets/cmu-horiz-white-trans.svg
```


```xml
<p:pic>
<p:nvPicPr>
    <p:cNvPr id="1027" name="Picture 3" descr="_Plaid-Digital_FINAL-NEW.png"/>
    <p:cNvPicPr>
    <a:picLocks noChangeAspect="1"/>
    </p:cNvPicPr>
    <p:nvPr/>
</p:nvPicPr>
<p:blipFill>
    <a:blip r:embed="rId9">
    <a:extLst>
        <a:ext uri="{28A0092B-C50C-407E-A947-70E740481C1C}">
        <a14:useLocalDpi xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" val="0"/>
        </a:ext>
    </a:extLst>
    </a:blip>
    <a:srcRect l="59550" t="20876" r="39888" b="2893"/>
    <a:stretch>
    <a:fillRect/>
    </a:stretch>
</p:blipFill>
<p:spPr bwMode="auto">
    <a:xfrm rot="5400000">
    <a:off x="3798887" y="1046163"/>
    <a:ext cx="60325" cy="7658100"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
    <a:avLst/>
    </a:prstGeom>
    <a:noFill/>
    <a:ln>
    <a:noFill/>
    </a:ln>
    <a:extLst>
    <a:ext uri="{909E8E84-426E-40DD-AFC4-6F175D3DCCD1}">
        <a14:hiddenFill xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main">
        <a:solidFill>
            <a:srgbClr val="FFFFFF"/>
        </a:solidFill>
        </a14:hiddenFill>
    </a:ext>
    <a:ext uri="{91240B29-F687-4F45-9708-019B960494DF}">
        <a14:hiddenLine xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" w="9525">
        <a:solidFill>
            <a:srgbClr val="000000"/>
        </a:solidFill>
        <a:miter lim="800000"/>
        <a:headEnd/>
        <a:tailEnd/>
        </a14:hiddenLine>
    </a:ext>
    </a:extLst>
</p:spPr>
</p:pic>
<p:pic>
<p:nvPicPr>
    <p:cNvPr id="1029" name="Picture 3" descr="_Plaid-Digital_FINAL-NEW.png"/>
    <p:cNvPicPr>
    <a:picLocks noChangeAspect="1"/>
    </p:cNvPicPr>
    <p:nvPr userDrawn="1"/>
</p:nvPicPr>
<p:blipFill>
    <a:blip r:embed="rId9">
    <a:extLst>
        <a:ext uri="{28A0092B-C50C-407E-A947-70E740481C1C}">
        <a14:useLocalDpi xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" val="0"/>
        </a:ext>
    </a:extLst>
    </a:blip>
    <a:srcRect l="59550" t="20876" r="39888" b="2893"/>
    <a:stretch>
    <a:fillRect/>
    </a:stretch>
</p:blipFill>
<p:spPr bwMode="auto">
    <a:xfrm rot="5400000">
    <a:off x="3798887" y="1046163"/>
    <a:ext cx="60325" cy="7658100"/>
    </a:xfrm>
    <a:prstGeom prst="rect">
    <a:avLst/>
    </a:prstGeom>
    <a:noFill/>
    <a:ln>
    <a:noFill/>
    </a:ln>
    <a:extLst>
    <a:ext uri="{909E8E84-426E-40DD-AFC4-6F175D3DCCD1}">
        <a14:hiddenFill xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main">
        <a:solidFill>
            <a:srgbClr val="FFFFFF"/>
        </a:solidFill>
        </a14:hiddenFill>
    </a:ext>
    <a:ext uri="{91240B29-F687-4F45-9708-019B960494DF}">
        <a14:hiddenLine xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" w="9525">
        <a:solidFill>
            <a:srgbClr val="000000"/>
        </a:solidFill>
        <a:miter lim="800000"/>
        <a:headEnd/>
        <a:tailEnd/>
        </a14:hiddenLine>
    </a:ext>
    </a:extLst>
</p:spPr>
</p:pic>
```