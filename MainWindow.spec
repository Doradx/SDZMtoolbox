# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['MainWindow.py'],
             pathex=['S:\ImportantFileSync\Study\Graduate\1.科研\2020.11.29SURF-ImageAlignment-ShearFailureRegionDetermination\pyqt'],
             binaries=[],
             datas=[('res','res')],
             hiddenimports=['sklearn.utils._cython_blas', 'sklearn.neighbors.typedefs', 'sklearn.neighbors.quad_tree', 'sklearn.tree._utils', 'skimage.feature._orb_descriptor_positions', 'pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SDZM_v2.0.0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='res\\icons\\logo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='MainWindow')
