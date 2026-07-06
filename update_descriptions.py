#!/usr/bin/env python3
"""
Update EUM rule descriptions in icode-f90-rules.xml and icode-f77-rules.xml.
Replaces the generic "EUM Fortran Coding Rule: EUM.XXX.YYY" descriptions
with rich HTML descriptions sourced from fortran-rules.md.
"""

import re

# Mapping of rule key -> (rule_id, title, html_description)
# Descriptions are in HTML as SonarQube renders HTML in rule descriptions.
RULES = {
    "EUM.BLOC.NamedLoops": (
        "EUM-FCRule-1490",
        "Named loops",
        """<p>Named loops shall be used to aid visual matching of the DO and END DO statements when there are multiple levels of nested loops or when EXIT or CYCLE statements are used.</p>
<h3>Example</h3>
<pre>name: DO iVar = iStart, iFinish [,iStep]
   &lt;statements&gt;
END DO name</pre>
<h3>Implementation</h3>
<p>This rule flags unnamed DO loops when nesting depth is 2 or more, or when EXIT/CYCLE is used inside a DO loop.</p>"""
    ),
    "EUM.BLOC.WhereElse": (
        "EUM-FCRule-1470",
        "WHERE constructs with ELSE WHERE option",
        """<p>WHERE constructs with ELSE WHERE options shall have an empty ELSE WHERE option.</p>
<h3>Example</h3>
<pre>[name:] WHERE (&lt;condition&gt;)
  &lt;statements&gt;
[[ELSE WHERE (&lt;condition&gt;)
  &lt;statements&gt;]
ELSE WHERE
  &lt;statements&gt;]
END WHERE [name]</pre>"""
    ),
    "EUM.DESIGN.ModuleStructure": (
        "EUM-FCRule-0180",
        "Module files structure",
        """<p>Each MODULE shall consist of the following components:</p>
<ul>
<li>MODULE xxxx statement</li>
<li>Software file header</li>
<li>Module dependencies (with USE statement)</li>
<li>IMPLICIT NONE statement</li>
<li>PRIVATE statement</li>
<li>Definition of PUBLIC elements</li>
<li>Local variables, constants and types declaration</li>
<li>Data initialisation</li>
<li>CONTAINS</li>
<li>Body of the module, with the codification of all procedures</li>
<li>END MODULE (full form)</li>
</ul>
<h3>Implementation</h3>
<p>This rule checks for the presence of key required sections: IMPLICIT NONE, PRIVATE, CONTAINS, and END MODULE in full form (not bare END).</p>"""
    ),
    "EUM.DESIGN.NoGlobalVars": (
        "EUM-FCRule-0730",
        "Modules and global variables",
        """<p>MODULEs shall not be used for global variables.</p>
<p>This is bad programming practice and makes maintenance of the source code very difficult.</p>
<h3>Implementation</h3>
<p>This rule flags modules that contain variable declarations but no CONTAINS section (i.e., pure data modules with no procedures, which likely indicate global variable misuse).</p>"""
    ),
    "EUM.DESIGN.OneUnitPerFile": (
        "EUM-FCRule-0110",
        "Software file content",
        """<p>Each programming unit (PROGRAM or MODULE) shall be in a different file.</p>
<h3>Implementation</h3>
<p>This rule checks that each file contains only one programming unit (PROGRAM or MODULE). It flags files that contain both a PROGRAM and a MODULE, or more than one MODULE or PROGRAM.</p>"""
    ),
    "EUM.DESIGN.ProgramStructure": (
        "EUM-FCRule-0170",
        "Program files structure",
        """<p>Each PROGRAM shall consist of the following components:</p>
<ul>
<li>PROGRAM xxxx statement</li>
<li>Software file header</li>
<li>Module dependencies (with USE statement)</li>
<li>IMPLICIT NONE statement</li>
<li>Local types, variables and constants declarations</li>
<li>Data initialisation</li>
<li>Body of the program</li>
<li>CONTAINS statement (optional)</li>
<li>Local subroutines and functions (optional)</li>
<li>END PROGRAM statement (full form)</li>
</ul>
<h3>Implementation</h3>
<p>This rule checks for the presence of key required sections: IMPLICIT NONE and END PROGRAM in full form (not bare END).</p>"""
    ),
    "EUM.DESIGN.SubroutineStructure": (
        "EUM-FCRule-0190",
        "Subroutines and functions content",
        """<p>A FORTRAN function or subroutine shall consist of the following:</p>
<ul>
<li>Subroutine header</li>
<li>Subroutine xxxx definition</li>
<li>Declaration of arguments</li>
<li>Local definitions</li>
<li>Executable block</li>
<li>FORMAT statements</li>
<li>END SUBROUTINE xxxx statement</li>
</ul>
<h3>Example</h3>
<pre>!-------------------------------------------------------------------------------
! Name:
! Purpose:
! Argument I/O:
! Returns:
!-------------------------------------------------------------------------------

SUBROUTINE mySubroutine( in_rX, in_rY )

!---USE statements--------------------------------------
...
!---End of USE statements-------------------------------

!---Declaration of arguments----------------------------
  REAL, INTENT(IN)           :: in_rX
  REAL, INTENT(IN), OPTIONAL :: in_rY
  ...
!---End of declaration of arguments---------------------

!---Declaration of local variables----------------------
  INTEGER :: iInteger
  REAL    :: rReal
...
!---End of declaration of local variables---------------

!---Executable block------------------------------------
...
!---End of executable block-----------------------------

!---Format block----------------------------------------
...
!---End of format block---------------------------------

END SUBROUTINE mySubroutine</pre>
<h3>Implementation</h3>
<p>This rule checks for the presence of a header before the definition and END SUBROUTINE in full form (not bare END).</p>"""
    ),
    "EUM.FILE.HeaderContent": (
        "EUM-FCRule-0500",
        "Software file header",
        """<p>Each programming unit (PROGRAM or MODULE) shall have a header with, at least, the following components:</p>
<ul>
<li>Unique identification of the module concerned</li>
<li>Unique identification of the file</li>
<li>Author's name</li>
<li>Statement of the Copyright ownership of the code</li>
<li>Description - description of the nature of functions/subroutines in this file</li>
</ul>
<h3>Example</h3>
<pre>!-------------------------------------------------------------------------------
! Component Name:  component name
! File: file name (it may be automatically inserted by the code management tool)
! Author: author name
! Copyright: EUMETSAT 2015
! Description: brief description of the purpose of the file content (e.g. class
!              description)
!-------------------------------------------------------------------------------</pre>
<h3>Implementation</h3>
<p>This rule validates that the file header contains the required fields: Component Name, File, Author, Copyright, and Description.</p>"""
    ),
    "EUM.INST.ArgOrder": (
        "EUM-FCRule-0820",
        "Input / Output order",
        """<p>IN parameters shall be passed first, then INOUT parameters, then finally OUT parameters.</p>"""
    ),
    "EUM.INST.ArgTypeDecl": (
        "EUM-FCRule-0810",
        "Input / Output declaration",
        """<p>All input and output arguments shall have declared data types.</p>
<h3>Implementation</h3>
<p>This rule checks that all dummy arguments (from the SUBROUTINE/FUNCTION signature) have an explicit data type declaration in the procedure body.</p>"""
    ),
    "EUM.INST.Backspace": (
        "EUM-FCRule-1670",
        "No BACKSPACE",
        """<p>BACKSPACE shall not be used.</p>"""
    ),
    "EUM.INST.BlockData": (
        "EUM-FCRule-1100",
        "No BLOCK DATA",
        """<p>BLOCK DATA shall not be used. Use modules instead.</p>"""
    ),
    "EUM.INST.CharLen": (
        "EUM-FCRule-1040",
        "Character string variables",
        """<p>Character string variables shall use the LEN=[number] attribute.</p>
<h3>Example</h3>
<pre>CHARACTER(LEN=128) :: cString</pre>
<h3>Implementation</h3>
<p>This rule checks that character variables use the LEN=n attribute, not the *n notation. For example, <code>character(len=10)</code> is OK, but <code>character*10</code> is not.</p>"""
    ),
    "EUM.INST.CompilerExt": (
        "EUM-FCRule-1800",
        "Compiler extensions",
        """<p>No compiler- or platform-dependent extensions shall be used.</p>
<h3>Implementation</h3>
<p>This rule detects the following compiler extension pragmas and non-standard features: <code>!DEC$</code>, <code>!DIR$</code>, <code>!GCC$</code>, <code>BYTE</code>, <code>%VAL</code>, <code>%REF</code>, <code>%LOC</code>.</p>"""
    ),
    "EUM.INST.Continuation": (
        "EUM-FCRule-1810",
        "Continuation Character",
        """<p>The continuation character shall be an ampersand and shall be placed only at the end of each line that is to be continued.</p>
<h3>Example</h3>
<pre>1000 FORMAT (1x, 'APLHA', 5x, 'BETA', 5x, 'GAMMA', &
             5x, 'DELTA')</pre>"""
    ),
    "EUM.INST.Continue": (
        "EUM-FCRule-1530",
        "CONTINUE statement",
        """<p>CONTINUE shall not be used.</p>
<h3>Implementation</h3>
<p>This rule detects standalone CONTINUE statements (not END CONTINUE).</p>"""
    ),
    "EUM.INST.DoubleColon": (
        "EUM-FCRule-1030",
        "Double colon",
        """<p>Double colon (::) shall be used to declare a variable (even without attributes).</p>
<h3>Example</h3>
<pre>INTEGER :: iIndex</pre>
<h3>Implementation</h3>
<p>This rule checks that <code>::</code> is present in all declarations. For example, <code>integer x</code> is a violation; it must be <code>integer :: x</code>.</p>"""
    ),
    "EUM.INST.DummyArgOrder": (
        "EUM-FCRule-0840",
        "Order of dummy arguments",
        """<p>Declaration of dummy arguments shall follow the same order in which they appear in the subroutine or function calling sequence.</p>"""
    ),
    "EUM.INST.EqvOperators": (
        "EUM-FCRule-1310",
        "Equivalence operators",
        """<p>Logical comparison operators (.EQV., .NEQV.) shall only be used to compare two logical variables. Never compare a logical variable with .TRUE. or .FALSE.</p>
<p>Use of .EQ. and .NE. on LOGICAL operands is not supported, except via compiler options, which is not recommended except for legacy code (where the behaviour expected by the code is assumed).</p>
<h3>Implementation</h3>
<p>This rule checks that .EQV./.NEQV. are not used with .TRUE./.FALSE. literals.</p>"""
    ),
    "EUM.INST.FormatPlacement": (
        "EUM-FCRule-1690",
        "FORMAT statement placement",
        """<p>FORMAT statements shall be placed at the end of the scope of the corresponding READ or WRITE statements, as described by the rule EUM-FCRule-0190.</p>"""
    ),
    "EUM.INST.FormatStmt": (
        "EUM-FCRule-1680",
        "READ & WRITE associated FORMAT",
        """<p>Format in the operations of reading and writing (READ and WRITE) shall use an associated FORMAT statement (rather than format specification directly in the READ or WRITE statement).</p>"""
    ),
    "EUM.INST.FreeFormatRead": (
        "EUM-FCRule-1700",
        "Space separated data reading",
        """<p>Reading of data shall be based on space separated data and free format READ. The use of formatted data reading should be limited to those cases in which data interpretation cannot be left to the compiler (FORMAT='*').</p>"""
    ),
    "EUM.INST.FunctionIntent": (
        "EUM-FCRule-0930",
        "FUNCTION's calling sequence",
        """<p>The calling sequence arguments of a function shall exclusively be of INTENT(IN) type.</p>"""
    ),
    "EUM.INST.Namelist": (
        "EUM-FCRule-1860",
        "Do not use NAMELIST",
        """<p>NAMELIST shall not be used.</p>"""
    ),
    "EUM.INST.NoData": (
        "EUM-FCRule-1150",
        "No DATA initialization",
        """<p>Initialisation with DATA shall be avoided.</p>"""
    ),
    "EUM.INST.NoLabelledDo": (
        "EUM-FCRule-1480",
        "Labelled loops",
        """<p>Labelled DO loops shall not be used.</p>
<h3>Example</h3>
<pre>      DO label iVar = iStart, iFinish [, iStep]
         &lt;statements&gt;
label CONTINUE</pre>"""
    ),
    "EUM.INST.NoSingleLineWhere": (
        "EUM-FCRule-1460",
        "No single line WHERE",
        """<p>Single line WHERE statements shall not be used. Use the form WHERE ... [ELSE WHERE ... ] END WHERE instead.</p>
<h3>Example</h3>
<pre>WHERE (&lt;condition&gt;) &lt;statement&gt;    ! WRONG

[name:] WHERE (&lt;condition&gt;)        ! RIGHT
  &lt;statements&gt;
[[ELSE WHERE (&lt;condition&gt;)
  &lt;statements&gt;]
ELSE WHERE
  &lt;statements&gt;]
END WHERE [name]</pre>"""
    ),
    "EUM.INST.NoUnderscoreKind": (
        "EUM-FCRule-1220",
        "No underscore + kind attribute",
        """<p>Qualification of constants and variables by means of underscore + kind attribute shall not be used.</p>
<h3>Example</h3>
<pre>DOUBLE PRECISION :: x
...
y = x_8    ! Not OK</pre>"""
    ),
    "EUM.INST.OneVarPerLine": (
        "EUM-FCRule-1010",
        "Only one variable declaration per line",
        """<p>Only one variable shall be declared per source code statement.</p>
<h3>Implementation</h3>
<p>This rule checks that only one variable is declared per <code>::</code> statement. For example, <code>integer :: a, b</code> is a violation.</p>"""
    ),
    "EUM.INST.OptionalAfterMandatory": (
        "EUM-FCRule-0850",
        "Dummy arguments after non-optional",
        """<p>OPTIONAL dummy arguments shall be declared after mandatory dummy arguments, following also the IN, INOUT, OUT orders.</p>"""
    ),
    "EUM.INST.OptionalDefault": (
        "EUM-FCRule-0940",
        "OPTIONAL attribute",
        """<p>Use of OPTIONAL attribute shall be restricted to the implementation of default parameters. The corresponding calling parameters must be of INTENT(IN) type and a default value must be assigned at the start of the procedure, if the respective actual parameter is not present in the procedure call. They shall appear after mandatory arguments.</p>"""
    ),
    "EUM.INST.OptionalNamed": (
        "EUM-FCRule-0830",
        "Explicitly identify OPTIONAL arguments",
        """<p>OPTIONAL arguments shall be explicitly identified in procedure calls by the name of the dummy argument associated to the name of the actual calling argument.</p>
<h3>Example</h3>
<pre>SUBROUTINE mySubroutine( x, y )
  REAL, INTENT(IN)           :: x
  REAL, INTENT(IN), OPTIONAL :: y
  ...
CALL mySubroutine( myX, y=myY )</pre>
<h3>Implementation</h3>
<p>This rule checks same-file procedure calls only (subroutine defined in the same file). Cross-file analysis is a candidate for future improvement.</p>"""
    ),
    "EUM.INST.PercentBlank": (
        "EUM-FCRule-1830",
        "Blank usage with %",
        """<p>Blanks shall not be used in identifiers before and after the % record field separator (i.e. DATA%ITEM, not DATA % ITEM).</p>"""
    ),
    "EUM.INST.PureFunc": (
        "EUM-FCRule-0950",
        "PURE SUBROUTINES & FUNCTIONS",
        """<p>In FORTRAN 95, SUBROUTINEs and FUNCTIONs shall have the PURE attribute when possible. It is desirable that subroutines are re-entrant (they have the same behaviour every time they are called).</p>
<h3>Implementation</h3>
<p>This rule uses a heuristic: if a FUNCTION has all INTENT(IN) arguments and no external I/O (no READ/WRITE), it should be marked PURE. Note: this may have false negatives as not all side effects can be detected.</p>"""
    ),
    "EUM.INST.Redundant": (
        "EUM-FCRule-1850",
        "Redundant features",
        """<p>The use of the following redundant FORTRAN 90 language features shall not be used:</p>
<ul>
<li>The D exponent letter for double precision numbers (e.g. 1.23D-45; use 1.23E-45 instead)</li>
<li>Common blocks (use modules instead)</li>
<li>Rational operators .EQ., .NE., .LT., .LE., .GT., .GE. (use ==, /=, &lt;, etc instead)</li>
<li>CONTINUE statement</li>
<li>Statement functions</li>
<li>CHARACTER*(*) declaration</li>
<li>ENTRY points</li>
<li>Real and Double precision DO control variables and DO loop control expressions</li>
<li>INCLUDE statements (use USE statement instead)</li>
</ul>
<p>Note: Most items are already covered by other specific EUM rules; this rule serves as a catch-all.</p>"""
    ),
    "EUM.INST.StringDim": (
        "EUM-FCRule-0870",
        "String dimensions of dummy arguments",
        """<p>Dimensions of character string as dummy arguments shall use the LEN attribute and the asterisk (*) to identify the length. This rule applies even to the cases in which the dimension of the character string is known inside the procedure. The use of asterisk (*) rather than a predefined dimension permits that the character string memory is properly passed to the procedure. Checks on the size of the actual calling argument can be performed inside the subroutine if necessary (with LEN and LEN_TRIM). Providing enough memory for the procedure call is caller responsibility.</p>
<h3>Example</h3>
<pre>SUBROUTINE name (A)
  CHARACTER(LEN=*)   :: A     ! OK
  CHARACTER(LEN=23)  :: A     ! Not OK</pre>"""
    ),
    "EUM.MET.MaxArguments": (
        "EUM-FCRule-2030",
        "Maximum number of arguments",
        """<p>Maximum number of arguments in a procedure shall be 10.</p>"""
    ),
    "EUM.MET.MaxAttributes": (
        "EUM-FCRule-2040",
        "Maximum number of attributes",
        """<p>Maximum number of attributes in an abstract type shall be 10.</p>"""
    ),
    "EUM.MET.MaxContinuation": (
        "EUM-FCRule-2050",
        "Maximum number of continuation lines",
        """<p>Maximum number of continuation lines shall be 10 (the maximum allowed in the standard is 39).</p>"""
    ),
    "EUM.MET.MaxProcedures": (
        "EUM-FCRule-2010",
        "Maximum number of procedures per module",
        """<p>Maximum number of procedures in a module shall be 20.</p>"""
    ),
    "EUM.NAME.Constants": (
        "EUM-FCRule-0410",
        "Constants",
        """<p>All constants shall contain no lower case characters (except the type indicator when using Hungarian notation) and shall be defined with the PARAMETER attribute.</p>
<h3>Example</h3>
<pre>DOUBLE PRECISION, PARAMETER :: TAUCONSTANT = 6.28318530718  ! Simple notation

DOUBLE PRECISION, PARAMETER :: rTAUCONSTANT = 6.28318530718 ! Hungarian notation</pre>"""
    ),
    "EUM.NAME.FileExt": (
        "EUM-FCRule-0150",
        "File extension",
        """<p>FORTRAN source files shall have an extension appropriate to the version being used.</p>
<h3>Example</h3>
<pre>.f90, F90, f95, F95, .f03...</pre>
<p>Which extension is to be applied is compiler dependent. For example, gfortran treats F90 source files differently to f90.</p>
<h3>Implementation</h3>
<p>This rule checks that the file extension is in the allowed list: <code>.f90</code>, <code>.F90</code>, <code>.f95</code>, <code>.F95</code>, <code>.f03</code>, <code>.F03</code>. Any other extension is flagged.</p>"""
    ),
    "EUM.NAME.FormatLabels": (
        "EUM-FCRule-1710",
        "FORMAT labels",
        """<p>Labels for FORMAT statements shall start at 1000 and increase by 10 for each statement.</p>"""
    ),
    "EUM.NAME.IdChars": (
        "EUM-FCRule-0320",
        "Identifier Characters",
        """<p>Identifiers shall consist only of the following characters:</p>
<ul>
<li>Upper case alphabetic letters [A...Z]</li>
<li>Lower case alphabetic letters [a...z]</li>
<li>Digits [0...9]</li>
<li>Underscore character</li>
</ul>
<p>FORTRAN compilers do not distinguish between upper and lower case. Case should be used to aid the readability of the names but cannot be used as the only difference between variable names.</p>"""
    ),
    "EUM.NAME.IdFormat": (
        "EUM-FCRule-0370",
        "Identifiers format",
        """<p>Identifiers shall be defined as <code>[scope_][type]&lt;name&gt;</code> where:</p>
<ul>
<li><code>[scope_]</code> This is a module identification key plus an underscore. This shall be omitted for identifiers which are local to a subroutine or function. It shall use the following convention:
<table>
<tr><th>Keyword</th><th>Scope</th></tr>
<tr><td>AAbb_</td><td>For public MODULE variables</td></tr>
<tr><td>bb_</td><td>For private MODULE variables</td></tr>
<tr><td>N/A</td><td>For local to a subroutine or function</td></tr>
</table>
Where the upper-case letters (AA) identify uniquely the library on which the module is located, and the lower-case letters (bb) identify uniquely the module inside the library.</li>
<li><code>[type]</code> Only when using Hungarian notation. It contains one or more lower case letters that identify the type of variable with the following convention, and in the specified order. This is omitted for MODULEs and Functions/Subroutines.
<table>
<tr><th>Prefix</th><th>Type</th><th>Comment</th></tr>
<tr><td>c</td><td>Character</td><td></td></tr>
<tr><td>i</td><td>Integer</td><td></td></tr>
<tr><td>r</td><td>Real / Double precision</td><td></td></tr>
<tr><td>x</td><td>Complex</td><td></td></tr>
<tr><td>l</td><td>Logical</td><td></td></tr>
<tr><td>t</td><td>Type (Structure)</td><td></td></tr>
<tr><td>a</td><td>Array</td><td>It can be used in combination with other prefixes.</td></tr>
<tr><td>p</td><td>Pointer</td><td>It can be used in combination with other prefixes.</td></tr>
</table>
</li>
<li><code>&lt;name&gt;</code> Is a meaningful name. It shall:
<ul>
<li>contain only capital letters for constants (e.g. SOMECONSTANT) or</li>
<li>use CamelCase format, starting always with uppercase, for the rest of identifiers (e.g. LoopCounter).</li>
</ul>
Underscore characters shall not be used in function or variable meaningful names.</li>
</ul>
<h3>Example</h3>
<pre>ORbt_iLoopCounter: Integer in the Orbit module.
                   Public MODULE variable
es_arQuaternion:   Array of Real in the Attitude Estimation module.
                   Private MODULE variable
iNumClouds:        Integer counter of number of clouds. Local variable.
iTAUCONSTANT:      Integer constant. Local variable</pre>"""
    ),
    "EUM.NAME.IdLength": (
        "EUM-FCRule-0330",
        "Identifier Length",
        """<p>A limitation of 32 characters shall be imposed on all identifier names.</p>"""
    ),
    "EUM.NAME.IdScope": (
        "EUM-FCRule-0400",
        "Identifiers format scope",
        """<p>Identifiers format shall apply to:</p>
<ul>
<li>Modules</li>
<li>Functions/subroutines</li>
<li>Variables</li>
<li>Types and structures</li>
</ul>
<h3>Implementation</h3>
<p>This is a meta-rule ensuring that EUM.NAME.IdFormat applies to Modules, Functions/subroutines, Variables, and Types/structures. It is implemented as part of the EUM.NAME.IdFormat checker.</p>"""
    ),
    "EUM.NAME.ModuleName": (
        "EUM-FCRule-0130",
        "MODULE names",
        """<p>The name of the MODULE shall follow the format AAbb_Name. Where:</p>
<ul>
<li>The two upper-case letters (AA) shall identify uniquely the library on which the module is located.</li>
<li>The lower-case letters (bb) shall identify uniquely the module inside the library.</li>
<li>Name shall be a meaningful identifier, using CamelCase notation.</li>
</ul>
<h3>Example</h3>
<p>File CLvi_CloudVisualization.f90</p>
<pre>MODULE CLvi_CloudVisualization
...
END MODULE</pre>"""
    ),
    "EUM.NAME.PrivateFormat": (
        "EUM-FCRule-0390",
        "Private elements format",
        """<p>All elements in the module scope (PRIVATE) should be only prefixed with the module identification, followed by an underscore.</p>
<h3>Example</h3>
<pre>mm_myModuleConstant</pre>"""
    ),
    "EUM.NAME.ProgramName": (
        "EUM-FCRule-0120",
        "PROGRAM names",
        """<p>The name of the PROGRAM shall be a meaningful identifier, using CamelCase notation.</p>
<h3>Example</h3>
<p>File Orbit.f90</p>
<pre>PROGRAM Orbit
...
END PROGRAM</pre>"""
    ),
    "EUM.NAME.PublicFormat": (
        "EUM-FCRule-0380",
        "Public elements format",
        """<p>All PUBLIC elements within a module should be prefixed in the same manner as the module they belong to.</p>
<h3>Example</h3>
<pre>LLmm_iMyPublicVariable</pre>"""
    ),
    "EUM.PRES.BlankLines": (
        "EUM-FCRule-0610",
        "Blank lines",
        """<p>Blank lines shall be placed wherever they improve the appearance and layout of the code.</p>
<h3>Implementation</h3>
<p>This rule checks that there are no more than 2 consecutive blank lines.</p>"""
    ),
    "EUM.PRES.BlockAlign": (
        "EUM-FCRule-0240",
        "Control blocks justification",
        """<p>Control blocks shall be properly aligned. DO and END DO starting at the same column and the lines in between consistently indented to the right.</p>"""
    ),
    "EUM.PRES.CommentBlock": (
        "EUM-FCRule-0590",
        "Comment blocks",
        """<p>Comment blocks shall be placed at the start of blocks of calculations.</p>
<p>Comment blocks are one or more lines of text. They should typically be placed at the start of blocks of calculations, DO ... END DO loops, or larger IF ... END IF constructs. They should also be included wherever they will serve to clarify some lines of code.</p>
<h3>Example</h3>
<pre>!  Check all plates are within dimension limits
   lDimsok = .TRUE.
   DO iLoop = 1, iNumPlates
      rXpos = arCoord (1,iLoop)
      rYpos = arCoord (2,iLoop)
      rZpos = arCoord (3,iLoop)
      CALL CheckDim (rXpos, rZpos, lDimsok)
   END DO
!  iDimsok is now false if limits were exceeded.</pre>
<h3>Implementation</h3>
<p>This rule flags big (5 or more lines) IF/DO constructs that are not preceded by a comment. Smaller constructs (1 line or less) are skipped.</p>"""
    ),
    "EUM.PRES.CommentPos": (
        "EUM-FCRule-0520",
        "Comment positions",
        """<p>Comments shall be placed at the following positions:</p>
<ul>
<li>At the beginning of each iterative process or loop, as described by EUM-FCRule-0590.</li>
<li>Preceding a series of lines of code that make a clearly defined function</li>
<li>Preceding any logical process (IF, WHERE, SELECT CASE...)</li>
<li>Before calling a subroutine or function</li>
<li>Preceding any sentence or block of sentences for reading and writing</li>
<li>Declaration of variables (grouped by related functionality), as described by EUM-FCRule-0600.</li>
</ul>
<h3>Implementation</h3>
<p>This rule flags IF/DO/SELECT CASE/CALL/READ/WRITE statements not preceded by a comment line. Single-line comments count. Nearby violations are grouped to reduce noise.</p>"""
    ),
    "EUM.PRES.Doxygen": (
        "EUM-FCRule-0580",
        "Doxygen comments",
        """<p>Doxygen comment codes should be used when declaring a function.</p>
<h3>Example</h3>
<pre>!&gt; comment preceding function
  FUNCTION XXmm_MyFunction( x ) RESULT( res )</pre>
<h3>Implementation</h3>
<p>This rule checks that <code>!&gt;</code> is used before function declarations. The <code>!&lt;</code> notation is NOT allowed.</p>"""
    ),
    "EUM.PRES.IndentLevel": (
        "EUM-FCRule-0220",
        "Indentation level",
        """<p>Each level of indentation shall consist of two blank spaces.</p>"""
    ),
    "EUM.PRES.LabelJustify": (
        "EUM-FCRule-0230",
        "Labels justification",
        """<p>Labels shall be left justified to the same column to facilitate the browsing.</p>
<h3>Implementation</h3>
<p>This rule checks that all labels (statement numbers like 1000, 100) start at column 1.</p>"""
    ),
    "EUM.PRES.NoCommentMultiLine": (
        "EUM-FCRule-0550",
        "No comments between multi-line sentences",
        """<p>Comments shall not be inserted between sentences that are constituted by more than a line (with continuation lines).</p>"""
    ),
    "EUM.PRES.NoEmptyComment": (
        "EUM-FCRule-0570",
        "Do not use empty comment lines",
        """<p>Empty comment lines shall not be used. Use empty lines instead.</p>"""
    ),
    "EUM.PRES.NoEndLineComment": (
        "EUM-FCRule-0560",
        "Do not use end-of-line comments",
        """<p>End-of-line comments (comments at the end of code lines) shall not be used.</p>"""
    ),
    "EUM.PRES.NoTabs": (
        "EUM-FCRule-0210",
        "No TABS",
        """<p>The TAB character shall not be used. Use blank characters for indentation and spacing instead.</p>"""
    ),
    "EUM.PROJECT.HeaderContent": (
        "EUM-FCRule-0510",
        "Subroutines and function header",
        """<p>Each programming function or subroutine shall have a header with the following components:</p>
<ul>
<li>Routine name</li>
<li>Purpose of the routine</li>
<li>Description of the input/output argument</li>
<li>Description of the value returned</li>
</ul>
<h3>Example</h3>
<pre>!-------------------------------------------------------------------------------
! Name: function name
! Purpose: brief description of the purpose of the function
! Argument I/O: input/output arguments and affected global data with a brief
!               explanation of their meaning
! Returns: a brief explanation of the meaning of the returned value
!-------------------------------------------------------------------------------</pre>
<h3>Implementation</h3>
<p>This rule validates that the procedure header contains the required fields: Name, Purpose, Argument I/O, and Returns.</p>"""
    ),
    "EUM.TYPE.PrivateInType": (
        "EUM-FCRule-1160",
        "Abstract Types Declaration",
        """<p>Abstract types shall always contain the PRIVATE statement.</p>
<p>This is a good Object-Oriented practice to avoid incorrect set/get of the data.</p>
<h3>Example</h3>
<pre>TYPE AAbb_tStateVector
  PRIVATE
  DOUBLE PRECISION :: rEpoch
  DOUBLE PRECISION, DIMENSION(6) :: daData
END TYPE AAbb_tStateVector</pre>"""
    ),
}


def update_xml_file(filepath):
    """Replace generic EUM rule descriptions with rich HTML descriptions."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    replaced = 0
    for rule_key, (rule_id, title, html_desc) in RULES.items():
        # The old description pattern: <description>EUM Fortran Coding Rule: EUM.XXX.YYY</description>
        old_desc = f"EUM Fortran Coding Rule: {rule_key}"
        
        # Build the new description with CDATA
        full_desc = f"<![CDATA[\n<h2>{rule_id}: {title}</h2>\n{html_desc}\n]]>"
        
        old_str = f"<description>{old_desc}</description>"
        new_str = f"<description>{full_desc}</description>"
        
        if old_str in content:
            content = content.replace(old_str, new_str)
            replaced += 1
        else:
            print(f"  WARNING: Could not find description for {rule_key} in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  Updated {replaced}/{len(RULES)} rule descriptions in {filepath}")
    return replaced


if __name__ == "__main__":
    base = "/tcenas2/CO2M/user/co2m/dev/sonar-icode-cnes-plugin-fork/src/main/resources/rules"
    
    print("Updating F90 rules XML...")
    f90_count = update_xml_file(f"{base}/icode-f90-rules.xml")
    
    print("Updating F77 rules XML...")
    f77_count = update_xml_file(f"{base}/icode-f77-rules.xml")
    
    total = f90_count + f77_count
    print(f"\nDone! Total descriptions updated: {total} (expected: {len(RULES) * 2})")
    
    if total != len(RULES) * 2:
        print("WARNING: Not all descriptions were updated!")
