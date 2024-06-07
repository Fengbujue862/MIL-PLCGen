# MIL-PLCGen

this is the data and code of paper MIL-PLCGen
Here are four methods m1 m2 m3 m4 corresponding to the four experiments in the paper

## For M1:

use patterns_RAG-2.py generate pattern

use CTL_RAG-3.py generate CTL

use PLC_requirement_Chatbot-4.py fix pattern

use PLCCode_codebot-5.py generate ST code

use Pro_ST_fix.py fix ST code

## For M2:

use usecase_RAG-1.py generate usecase

use patterns_RAG-2.py generate pattern

use CTL_RAG-3.py generate CTL

use PLC_requirement_Chatbot-4.py fix pattern

use PLCCode_codebot-5.py generate ST code

use Pro_ST_fix.py fix ST code

## For M3:

use patterns_RAG-2.py generate pattern

use CTL_RAG-3.py generate CTL

use PLC_requirement_Chatbot-4.py fix pattern

use SMV_GEN.py generate SMV model

use SMV_fix_GEN.py fix SMV model

use ST_gen_codebot.py generate ST code

use Pro_ST_fix.py fix ST code

## For M4:

use usecase_RAG-1.py generate usecase

use patterns_RAG-2.py generate pattern

use CTL_RAG-3.py generate CTL

use PLC_requirement_Chatbot-4.py fix pattern

use ST_gen_codebot.py generate ST code

use Pro_ST_fix.py fix ST code



### support

For SMV verif we use NuSMV 2.6 you can download and learn form

https://nusmv.fbk.eu/downloads.html
For ST code verif we use PLCverid ou can download and learn form
https://gitlab.com/plcverif-oss/
