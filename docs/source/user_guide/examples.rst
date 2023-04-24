Examples
========

Exp Language
------------
:Source: :download:`exp </_static/exp.yaml>`

While not practical, the expression language provides a simple example using the tool.

.. raw:: html

  <div class="highlight" style="background: #0d1117;"><table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">1</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">2</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">3</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">4</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">5</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">6</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">7</span></pre></div></td><td class="code"><div><pre><span></span><span style="color: #a5d6ff">5</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">*</span><span style="color: #6e7681"> </span><span style="color: #c9d1d9">(</span><span style="color: #6e7681"></span>
  <span style="color: #6e7681">  </span><span style="color: #a5d6ff">3</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">+</span><span style="color: #6e7681"> </span><span style="color: #c9d1d9">(</span><span style="color: #6e7681"></span>
  <span style="color: #6e7681">    </span><span style="color: #c9d1d9">(</span><span style="color: #a5d6ff">4</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">-</span><span style="color: #6e7681"> </span><span style="color: #c9d1d9">(</span><span style="color: #6e7681"></span>
  <span style="color: #6e7681">      </span><span style="color: #a5d6ff">1</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">+</span><span style="color: #6e7681"> </span><span style="color: #a5d6ff">4</span><span style="color: #6e7681"></span>
  <span style="color: #6e7681">    </span><span style="color: #c9d1d9">))</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">*</span><span style="color: #6e7681"> </span><span style="color: #a5d6ff">2</span><span style="color: #6e7681"></span>
  <span style="color: #6e7681">  </span><span style="color: #c9d1d9">)</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">)</span><span style="color: #6e7681"> </span><span style="color: #ff7b72; font-weight: bold">+</span><span style="color: #6e7681"> </span><span style="color: #a5d6ff">1</span><span style="color: #6e7681"></span>
  </pre></div></td></tr></table></div>


Gantt Language
--------------
:Source: :download:`gantt </_static/gantt.yaml>`

The Gantt language can be used to create LaTeX Gantt charts.

.. raw:: html

  <div class="highlight" style="background: #0d1117"><table class="highlighttable"><tr><td class="linenos"><div class="linenodiv"><pre><span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 1</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 2</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 3</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 4</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 5</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 6</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 7</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 8</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;"> 9</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">10</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">11</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">12</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">13</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">14</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">15</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">16</span>
  <span style="color: #6e7681; background-color: #0d1117; padding-left: 5px; padding-right: 5px;">17</span></pre></div></td><td class="code"><div><pre><span></span><span style="color: #a5d6ff">rows</span><span style="color: #c9d1d9">:</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">  </span><span style="color: #a5d6ff">Objective A</span><span style="color: #c9d1d9">:</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">    - </span><span style="color: #a5d6ff">inline</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">  </span><span style="color: #a5d6ff">Objective B</span><span style="color: #c9d1d9">:</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">    - </span><span style="color: #a5d6ff">inline</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">---</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">                  </span><span style="color: #a5d6ff">Project Schedule</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">-------------------------------------------------</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">            |</span><span style="color: #a5d6ff">Oct</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Nov</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Dec</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Jan</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Feb</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Mar</span><span style="color: #c9d1d9">|</span><span style="color: #a5d6ff">Apr</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Objective A</span><span style="color: #c9d1d9"> |</span><span style="color: #ff7b72; font-weight: bold">~~~~~~~~~~</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Task One</span><span style="color: #c9d1d9">    |</span><span style="color: #79c0ff; font-weight: bold">======</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Task Two</span><span style="color: #c9d1d9">    |    </span><span style="color: #79c0ff; font-weight: bold">======</span><span style="color: #c9d1d9">&lt;&gt;</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Objective B</span><span style="color: #c9d1d9"> |             </span><span style="color: #ff7b72; font-weight: bold">~~~~~~~~~~~~~</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Task Three</span><span style="color: #c9d1d9">  |             </span><span style="color: #79c0ff; font-weight: bold">===</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Task Four</span><span style="color: #c9d1d9">   |                </span><span style="color: #79c0ff; font-weight: bold">=========</span><span style="color: #6e7681"></span>
  <span style="color: #a5d6ff">Task Five</span><span style="color: #c9d1d9">   |                      </span><span style="color: #79c0ff; font-weight: bold">====</span><span style="color: #c9d1d9">&lt;</span><span style="color: #a5d6ff">Finished</span><span style="color: #c9d1d9">&gt;</span><span style="color: #6e7681"></span>
  <span style="color: #c9d1d9">---------------------------------------------------</span><span style="color: #6e7681"></span>
  </pre></div></td></tr></table></div>

.. code-block:: latex

  \noindent\resizebox{\textwidth}{!}{%
  \begin{ganttchart}[vgrid,hgrid,x unit = 1cm,y unit chart = 1cm,bar/.append style={fill = lightgray}]{0}{27}
  \gantttitle{Project Schedule}{28}
  \\
  \gantttitle{Oct}{4}
  \gantttitle{Nov}{4}
  \gantttitle{Dec}{4}
  \gantttitle{Jan}{4}
  \gantttitle{Feb}{4}
  \gantttitle{Mar}{4}
  \gantttitle{Apr}{4}
  \\
  \ganttgroup[inline]{Objective A}{0}{9}
  \\
  \ganttbar{Task One}{0}{5}
  \\
  \ganttbar{Task Two}{4}{9}
  \ganttmilestone[inline]{}{9}
  \\
  \ganttgroup[inline]{Objective B}{13}{25}
  \\
  \ganttbar{Task Three}{13}{15}
  \\
  \ganttbar{Task Four}{16}{24}
  \\
  \ganttbar{Task Five}{22}{25}
  \ganttmilestone[inline]{Finished}{25}
  \end{ganttchart}%
  }


.. image:: /_static/example-gantt.png