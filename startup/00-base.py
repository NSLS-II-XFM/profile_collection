import nslsii

nslsii.configure_base(get_ipython().user_ns, 
        'xfm',
        publish_documents_with_kafka=True)

#nslsii.configure_olog(get_ipython().user_ns)

#Optional: set any metadata that rarely changes.
RE.md['beamline_id'] = 'XFM'

