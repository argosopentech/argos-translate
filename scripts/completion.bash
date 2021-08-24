#/usr/bin/env bash

# Tab Completion for argostranslate
_argostranslate_completions ()  
{
  local cur

  COMPREPLY=()
  cur=${COMP_WORDS[COMP_CWORD]}

  COMPREPLY=( $( compgen -W '--from-lang --to-lang --help' -- $cur ) )

  case "$cur" in
    -*)
    COMPREPLY=( $( compgen -W '--from-lang --to-lang --help' -- $cur ) );;

    ?)
    COMPREPLY=( $( compgen -W 'en ar zh nl fr de hi id ga it ja ko pl pt ru es tr uk vi' -- $cur ) );;

  esac

  return 0
}


# Tab Completion for argospm
_argospm_completions ()
{
  local cur

  COMPREPLY=($(compgen -W "update install list remove help" "${COMP_WORDS[1]}"))

  return 0
}


complete -F _argospm_completions argospm
complete -F _argostranslate_completions argos-translate argos-translate-cli
