<html>
<table cellpadding="0" cellspacing ="0">
  <tbody>
    <tr>
      <td><img src="MathCat.bmp" alt="Gizmo" width="150" height="150"></td>
      <td><h1>Math Cat</h1><h3>Calculator application</h3></td>
    </tr>
  </tbody>
</table>
  
<p>This calculator application is being designed to be as cross platform as possible. It works in three ways; you have a basic calaculator, a handwriting recognition calculator, and a database of equations calculator.</p>
</br>
<h3>Installing Tesseract and PyTesser</h3>

1. Install tesseract using windows installer available at: https://github.com/UB-Mannheim/tesseract/wiki
2. Note the tesseract path from the installation. Default installation path would be: C:\Program Files (x86)\Tesseract-OCR
3. pip install pytesseract
4. set the tesseract path in the script before calling image_to_string:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

There are other ways to get and install tesseract, but the Mannheim is the easiest for Windows computers.
</br>
<h3>Screenshots</h3>
<table cellpadding="0" cellspacing="0">
  <tbody>
    <tr>
      <td align="center"><img src='Screenshot (11).png' width="50%" height="50%"></td>
      <td align="center"><img src='Screenshot (10).png' width="50%" height="50%"></td>
    </tr>
  </tbody>
</table>
</html>
