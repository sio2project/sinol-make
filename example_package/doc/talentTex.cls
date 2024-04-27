% Latex style for Talent (https://talent.edu.pl) statemnts
% 
% Copyright (c) Stanisław Czech 2024
% Copyright (c) Jakub Rożek 2024
% Provided under MIT licence 
%
% Based on sinol.cls made by:
% Grzegorz Jakacki, Tomasz Waleń, Marcin Kubica, Jakub Pawlewicz
% Adam Iwanicki, Szymon Acedanski, Tomasz Idziaszek, Jakub Radoszewski


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Formalności
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\NeedsTeXFormat{LaTeX2e}
\def\sinolVersion{0.0.5}
\ProvidesClass{talentTex}[Stowarzyszenie Talent \sinolVersion]

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Include pakietów
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\RequirePackage[T1]{fontenc}
\RequirePackage{epsf}
\RequirePackage{graphicx}
\RequirePackage{ifpdf}
\RequirePackage{fancyhdr}
\RequirePackage[latin2,utf8]{inputenc}
\RequirePackage{verbatim}
\RequirePackage{xcolor}
\RequirePackage{xstring}
\RequirePackage{xparse}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plików w paczce
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\def\sinolTestIn{../in}
\def\sinolTestOut{../out}
\def\sinolContestLogo{logo.jpg}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Kolory
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\definecolor{talentBrown}{RGB}{97, 31, 30}
\definecolor{talentBlue}{RGB}{0, 56, 117} % logo
% \definecolor{talentBlue}{RGB}{31, 101, 157} % środek
% \definecolor{talentBlue}{RGB}{31, 129, 189} % Jasny (SZU)
% \definecolor{talentBlue}{RGB}{31, 73, 125} % Ciemny

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% zmienne logiczne
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\newif\ifsinolshortages \sinolshortagesfalse % niedoprecyzowania
\newif\ifsinolerrors  \sinolerrorsfalse % bledy
\newif\ifmetric  \metrictrue  % czy drukowac metryke
\newif\ifsignaturedefed \signaturedefedfalse % czy zdefiniowano sygnature
\newif\ifdatedefed \datedefedfalse  % czy podano date
\newif\ifetapdefed \etapdefedfalse  % czy podano etap
\newif\ifkonkursdefed \konkursdefedfalse  % czy podano konkurs
\newif\ifdaydefed \daydefedfalse  % czy podano dzień
\newif\ifgroupdefed \groupdefedfalse  % czy podano grupę
\newif\ifMemorydefed \Memorydefedfalse  % czy podano dostępną pamięć
\newif\iftimedefed \timedefedfalse % czy podano czas działania

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Obsługa plików: inf, err
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chardef\inffile=15 % plik wejsciowy (np. testy)
\chardef\errfile=14 % plik wyjsciowy
\chardef\tmpfile=13 % plik tymczasowy

% \infoutput{<tekst>} --- wyprowadza do pliku informacyjnego
\newcommand{\infoutput}[1]{%
  \immediate\write\inffile{#1}
}

% \erroutput{<tekst>} --- wyprowadza do pliku z bledami
\newcommand{\erroutput}[1]{%
  \immediate\write\errfile{#1}
  \global\sinolerrorstrue
}

% \erroutputWrongSection{<jest>}{<winno byc>} --- 
% wyprowadza informacje o blednej nazwie rodzialu
\newcommand{\erroutputWrongSection}[2]{%
  \erroutput{bledna nazwa lub lokalizacja rozdzialu '#1', spodziewane '#2'}%
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Czynności przed i po - otwiera pliki inf err
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\AtBeginDocument{%
  \immediate\openout\inffile \jobname.inf
  \immediate\openout\errfile \jobname.err
}

\AtEndDocument{%
  \ifsinolerrors
    \immediate\write16{SINOL: znaleziono bledy (zob. \jobname.err) !}
  \fi
  \ifsinolshortages
    \immediate\write16{SINOL: znaleziono niedoprecyzowania (wystepuje '[[[...]]]')}
  \fi
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Definicje
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\ucase#1{\expandafter\uppercase\expandafter{#1}}
\def\lcase#1{\expandafter\lowercase\expandafter{#1}}

\def\?#1{
  [[#1]]
}

\def\ifundef#1#2#3{
  \expandafter
  \ifx\csname#1\endcsname\relax
    #2
  \else
    #3
  \fi
}

\def\ifeq#1#2#3{
  \edef\@tempeqa{#1}
  \edef\@tempeqb{#2}
  \ifx\@tempeqa\@tempeqb
    #3
  \fi
}

\def\ifneq#1#2#3{
  \edef\@tempeqa{#1}
  \edef\@tempeqb{#2}
  \ifx\@tempeqa\@tempeqb\else
    #3
  \fi
}

\newcommand{\iffileexists}[3]{
  \immediate\openin\tmpfile #1\par
  \ifeof\tmpfile
    \immediate\closein\tmpfile
    #3
  \else
    \immediate\closein\tmpfile
    #2
  \fi
}

\newcommand{\twocol}[2]{
  \noindent
  \begin{minipage}[t]{0.5\textwidth}
  {#1}
  \end{minipage}\hfill
  \begin{minipage}[t]{0.5\textwidth}
  {#2}
  \end{minipage}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\def\LOGO{
  \leavevmode
  \hbox{
    \vbox to 0pt{
      \vss
      \hbox{
        \includegraphics[height=1.143cm,bb=0 0 900 300]{\sinolContestLogo}%
      }
    }
  }
}

\def\tophugetitle{
  \begin{minipage}[t]{0.8\textwidth}
    \setlength{\parindent}{-4pt}
    \color{talentBlue}
    \fontfamily{ptm}
    \huge
    \textbf{\sinolTitle}
  \end{minipage}
}

\def\topinformationbar{}

\def\sinolHistory{}
\def\sinolSignature{}

% uruchamiane po przeczytaniu deklaracji
\newcommand{\concludedecls}{
  % Sprawdzanie istnienia definicji
  \ifundef{ID}{
    \erroutput{brak 3-literowego identyfikatora (klauzula \string\id)}
    \def\ID{XXX}
  }{}
  \def\infile{{\ttfamily \lcase{\ID}.in}}
  \def\outfile{{\ttfamily \lcase{\ID}.out}}
  \ifundef{sinolTitle}{
    \erroutput{brak tytułu (klauzula \string\title)}
    \def\sinolTitle{\?{brak tytułu}}
  }{}
  \def\sinolIdSignature{\ucase{\ID}}
  \let\oldsection\section
}

% uruchamiane po przeczytaniu tekstu
\newcommand{\concludetext}{}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Przypisanie stałych przez użytkownika
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand{\id}[1]{
  \edef\ID{#1}
  \infoutput{[id][#1]}
}

\renewcommand{\title}[1]{
  \def\sinolTitle{#1}
  \infoutput{[title][#1]}
}

\newcommand{\signature}[1]{
  \def\sinolSignature{#1}
  \infoutput{[signature][#1]}
  \global\signaturedefedtrue
}

\newcommand{\history}[3]{
  \edef\sinolHistory{\noindent $\bullet$\ v.\,#3: #1, #2\par\sinolHistory}
  \infoutput{[history][#1][#2][#3]}
  \DocVersiondefedtrue
}

\newcommand{\etap}[1]{
  \def\sinolEtap{#1}
  \global\etapdefedtrue
}

\newcommand{\konkurs}[1]{
  \def\sinolKonkurs{#1}
  \global\konkursdefedtrue
}

\renewcommand{\day}[1]{
  \def\sinolDay{#1}
  \global\daydefedtrue
}

\newcommand{\group}[1]{
  \def\sinolGroup{#1}
  \global\groupdefedtrue
}

\newcommand{\Memory}[1]{
  \def\sinolMemory{#1}
  \global\Memorydefedtrue
}

\newcommand{\Time}[1]{
  \def\sinolTime{#1}
  \global\timedefedtrue
}

\newcommand{\infile}{{\ttfamily XXX.IN}}
\newcommand{\outfile}{{\ttfamily XXX.IN}}

\newcommand{\iomode}[1]{
  \def\sinolIOmode{#1}
  \ifeq{#1}{files}{
    \gdef\sinolExampleInputText{Dla pliku wejściowego \infile:}
    \gdef\sinolExampleOutputText{poprawnym wynikiem jest plik wyjściowy \outfile{}:}    
  }
  \ifeq{#1}{stdin}{
    \gdef\sinolExampleInputText{{\color{talentBlue}\bf Wejście:}}
    \gdef\sinolExampleOutputText{{\color{talentBlue}\bf Wyjście:}}    
  }    
  \ifeq{#1}{outputonly}{
    \gdef\sinolExampleInputText{Wejście:}
    \gdef\sinolExampleOutputText{Wyjście:}    
  }    
  \ifeq{#1}{interactive}{
    % TODO: UPDATE THIS
    \gdef\sinolExampleInputText{Wejście:}
    \gdef\sinolExampleOutputText{Wyjście:}    
  }    
}
\iomode{stdin}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Nazwy wyświetlane (zmiana języka, narazie tu ręcznie)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\def\sinolSNamePrzyklad{Przykład}
\def\sinolSNameZadanie{Zadanie}
\def\sinolSNameWejscie{Wejście}
\def\sinolSNameWyjscie{Wyjście}
\def\sinolSNameRozwiazanieWzorcowe{Rozwiązanie wzorcowe}
\def\sinolSNameTesty{Testy}
\def\sinolSNameUwagi{Uwagi}
\def\sinolSNameHistory{HISTORIA}
\def\sinolSNameOpis{Opis rozwiązania}
\def\sinolSNameOpracowanie{Opracowanie}

\def\sinolTitleZadanie{Zadanie}
\def\sinolEtapText{etap}
\def\sinolGroupText{Grupa}
\def\sinolDayText{}
\def\sinolKonkursText{}
\def\sinolSourceText{Plik źródłowy}
\def\sinolMemoryText{Pamięć}
\def\sinolTimeText{Czas}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Opcje talentTex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\DeclareOption{zad}{
  \renewcommand{\topinformationbar}{
    \hbox to \hsize
    {
      \begin{minipage}[t]{1\textwidth}
      \setlength{\parindent}{-2pt}
      \def\@tempempty{}
      \bf
      \fontfamily{ptm}
      \color{talentBlue}
      %
      %% Konkurs pokazuje się tylko gdy jest niepusty
      \ifkonkursdefed
        \ifx\sinolKonkurs\@tempempty
        \else\sinolKonkursText\sinolKonkurs.\
        \fi
      \else\?{brak konkursu}\erroutput{brak konkursu}\fi
      %
      %% Dzień pokazuje się tylko gdy jest niepusty
      \ifdaydefed
        \ifx\sinolDay\@tempempty
        \else\sinolDayText\sinolDay.\
        \fi
      \else\?{brak dnia}\erroutput{brak dnia}\fi
      %
      % Grupa
      \ifgroupdefed
        \if\sinolGroup\@tempempty
        \else\sinolGroupText:\,\sinolGroup.\
        \fi
      \else\?{brak grupy}\erroutput{brak grupy}\fi
      %
      % Dostępna pamięć -- pokazuje sie tylko gdy
      % nie jest pusta i jest zdefiniowana
      \ifMemorydefed
        \ifx\sinolMemory\@tempempty
        \else\sinolMemoryText:\,\sinolMemory\,MB.\
        \fi
      \else\?{brak limitu pamięci}\erroutput{brak limitu pamięci}\fi
      % 
      %% Limit czasu -- pokazuje się tylko gdy nie jest pusty i jest zdefiniowany.
      \iftimedefed
        \ifx\sinolTime\@tempempty
        \else\sinolTimeText:\,\sinolTime\,s.\
        \fi
      \else\?{brak limitu czasu}\erroutput{brak limitu czasu}\fi
      \hfill
      \end{minipage}
    }
  }

}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\DeclareOption{opi}{
  \renewcommand{\topinformationbar}{
    \hbox to \hsize
    {
      \begin{minipage}[t]{1\textwidth}
      \setlength{\parindent}{-2pt}
      \def\@tempempty{}
      \bf
      \fontfamily{ptm}
      \color{talentBlue}
      \Large
      \sinolSNameOpis
      \hfill
      \end{minipage}
    }
  }
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\DeclareOption{opr}{
  \renewcommand{\topinformationbar}{
    \hbox to \hsize
    {
      \begin{minipage}[t]{1\textwidth}
      \setlength{\parindent}{-2pt}
      \def\@tempempty{}
      \bf
      \fontfamily{ptm}
      \color{talentBlue}
      \Large
      \sinolSNameOpracowanie
      \hfill
      \end{minipage}
    }
  }
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\PassOptionsToClass{a4paper}{article}
\LoadClass{article}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% rozmiar papieru
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\setlength{\textwidth}{168mm} % {180mm}
\setlength{\textheight}{265mm} % {257mm}
\setlength{\oddsidemargin}{0pt}
\setlength{\hoffset}{-4mm} % this means 1in-15mm
\setlength{\voffset}{-30mm} % this means 1in-15mm
\setlength{\topmargin}{0pt}
\setlength{\parskip}{0pt}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.4pt}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Wygląd dokumentu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\pagestyle{fancy}
\lfoot{Stowarzyszenie Talent (talent.edu.pl)}
\rfoot{\sinolTitle\ - \ID}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Definicja przestrzeni dokumentu: 'tasktext'
\newenvironment{tasktext}{
  \concludedecls
  % Tytuł
  \leftline{%
    \tophugetitle%
  }
  % Logo
  \rightline{
    \hbox to\hsize{\hfil\LOGO}
  }
  \smallskip
  % Linia
  {
    \color{talentBrown}
    \hrule height 2pt \relax
  }
  \smallskip
  \topinformationbar
  \bigskip
}{
  \concludetext
  \closeout\inffile
  \closeout\errfile
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Komendy dostępne w klasie talentTex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% komendy do obsługi plików

\newcommand{\includefile}[1]{
\vspace{-0.7em}
\verbatiminput{#1}
}

\newcommand{\exampleinput}[1]{
    \iffileexists{\sinolTestIn/\ID0#1.in}{
      \includefile{\sinolTestIn/\ID0#1.in}
    }{
      \smallskip
      \?{brak pliku {\ttfamily\ID0#1.in}}\par
      \erroutput{brak pliku '\ID0#1.in' w scieżce '\sinolTestIn'}
      \smallskip
    }
}

\newcommand{\exampleoutput}[1]{
  \iffileexists{\sinolTestOut/\ID0#1.out}{
    \includefile{\sinolTestOut/\ID0#1.out}
  }{
    \smallskip
    \?{brak pliku {\ttfamily\ID0#1.out}}\par
    \erroutput{brak pliku '\ID0#1.out' w scieżce '\sinolTestOut'}
    \smallskip
  }
}

\newcommand{\makeexampleinput}[1]{
  \noindent\sinolExampleInputText
  \exampleinput{#1}
}

\newcommand{\makeexampleoutput}[1]{
  \noindent\sinolExampleOutputText
  \exampleoutput{#1}
}

\newcommand{\makestandardexample}[1]{%
  \makeexampleinput{#1}%
  \makeexampleoutput{#1}%
}

\newcommand{\makecompactexample}[1]{
  \twocol{\makeexampleinput{#1}}{\makeexampleoutput{#1}}
  \vspace{15pt}
  \setlength\parskip{15pt}
  \par
  \setlength\parskip{0pt}
  \par
}

% pozostałe komendy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\newcommand{\start}{
  \begin{document}
  \begin{tasktext}
}

\newcommand{\finish}{
  \end{tasktext}
  \end{document}
}

\newlength{\imgwidth}

% podpis pod/nad obrazkiem
\newcommand{\imgcaption}[1]{
  \def\capwidth{\textwidth}
  \addtolength\capwidth{-1cm}
  \centerline{\begin{minipage}{\capwidth}\footnotesize #1\end{minipage}}
}

% rysunek #1-plik, #2-podpis, #3-gdzie podpis (t-na gorze, b-na dole)
\newcommand{\img}[3]{
  \def\tmpargthree{#3}
  \def\tmpb{b}
  \setlength\imgwidth{\textwidth}
  \addtolength\imgwidth{-2cm}
  \begin{center}
  \begin{minipage}{\imgwidth}
  \ifx\tmpargthree\tmpb
    $$\includegraphics[width=1\imgwidth]{#1}$$
    \hrule
    \smallskip
    \imgcaption{#2}
  \else
    \imgcaption{#2}
    \smallskip
    \hrule
    \smallskip
    $$\includegraphics[width=1\imgwidth]{#1}$$
  \fi
  \end{minipage}\end{center}
}

\newcommand{\timg}[2]{\img{#1}{#2}{t}}
\newcommand{\bimg}[2]{\img{#1}{#2}{b}}
\newcommand{\plainimg}[1]{$$\includegraphics{#1}$$}

\newcommand{\tSection}[1]{
  \tCustomSection{#1}{15pt}
}

\newcommand{\tsection}[1]{
  \tSection{#1}
}

\newcommand{\tSmallSection}[1]{
  {
    \setlength\parindent{0pt}
    \setlength\parskip{5pt}
    \par
    {
      \fontfamily{ptm}
      \color{talentBlue}
      \textbf{#1}
    }
  }
  \setlength\parskip{2pt}
  \par
}

\newcommand{\tCustomSection}[2]{
  {
    \setlength\parindent{0pt}
    \setlength\parskip{#2}
    \par
    {
      \fontfamily{ptm}
      \color{talentBlue}
      \Large
      \textbf{#1}
    }
  }
  \setlength\parskip{2pt}
  \par
}

\newcommand{\tc}[1]{%
  \ifmmode
    \StrLen{#1}[\textLength]
    \ifnum\textLength=1
      \textcolor{talentBlue}{\textbf{\fontfamily{ptm}\selectfont #1}}%
    \else
      \textcolor{talentBlue}{\mathbf{{\fontfamily{ptm}\selectfont #1}}}%
    \fi
  \else
    \textcolor{talentBlue}{\textbf{\fontfamily{ptm}\selectfont #1}}%
  \fi
}

\newcommand{\ocen}[1]{
  \begin{enumerate}
  \setlength\itemindent{-13pt}
  \fontfamily{ptm}
  #1
  \end{enumerate}
}

\newcommand{\testOcen}[2]{
  \item[] \textbf{\color{talentBlue}\ID#1: \ }{#2}
}

\newcommand{\ocenTable}[1]{
  \customOcenTable{|c|c|c|}{\tc{Nr}&\tc{Ograniczenia}&\tc{Punkty}}{#1}
}

\newcommand{\customOcenTable}[3]{
  \begin{center}
    \begin{tabular}{#1}
    \hline
    #2 \\
    \hline
    #3
    \end{tabular}
  \end{center}
}

\newcommand{\ocenRow}[1]{
  #1 \\ \hline
}

\newcommand{\ocenElement}[1]{
  \begin{tabular}{@{}c@{}}
  #1
  \end{tabular}
}
