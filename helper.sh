# source this file only

function set_templates_and_stack_names {
   local BASENAME=rds-log-dog
   local POSTFIX=""
   if [ ${PERSONAL_BUILD} == true ]; then
      POSTFIX="-${USER:0:3}"
   fi
   DST_BUCKET_STACK_NAME="${BASENAME}-s3${POSTFIX}"
   FUNCTION_STACK_NAME="${BASENAME}-lambda${POSTFIX}"
}

